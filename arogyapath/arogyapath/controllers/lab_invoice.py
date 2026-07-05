import frappe
from arogyapath.arogyapath.utils.gst import compute_invoice_taxes, validate_gstin

def validate(doc, method=None):
	"""Validate Lab Invoice"""
	# Auto-fetch addresses
	set_customer_address(doc)
	set_company_address(doc)
	
	# Auto-fetch GSTIN from addresses (fetch_from doesn't always trigger)
	set_address_gstin(doc)
	
	# Auto-set place of supply from customer address
	set_place_of_supply(doc)
	
	# GST validation and computation
	if doc.billing_address_gstin:
		validate_gstin(doc.billing_address_gstin, "Billing Address GSTIN")
	if doc.company_gstin:
		validate_gstin(doc.company_gstin, "Company GSTIN")
	compute_invoice_taxes(doc)
	compute_doctor_commission(doc)

def set_customer_address(doc):
	"""Auto-fetch primary billing address for Patient"""
	if not doc.patient:
		return
	
	# If customer_address already set, skip
	if doc.customer_address:
		return
	
	# Fetch patient_primary_address from Patient DocType
	primary_address = frappe.db.get_value("Patient", doc.patient, "patient_primary_address")
	
	if primary_address:
		doc.customer_address = primary_address
	else:
		# Fallback: Find any billing address linked to this patient
		address = frappe.db.sql("""
			SELECT a.name
			FROM `tabAddress` a
			INNER JOIN `tabDynamic Link` dl ON dl.parent = a.name
			WHERE dl.link_doctype = 'Patient'
			  AND dl.link_name = %s
			  AND a.disabled = 0
			  AND (a.is_primary_address = 1 OR a.address_type = 'Billing')
			ORDER BY a.is_primary_address DESC, a.creation DESC
			LIMIT 1
		""", doc.patient, as_dict=1)
		
		if address:
			doc.customer_address = address[0].name

def set_company_address(doc):
	"""Auto-fetch primary billing address for Pathology Lab"""
	if not doc.pathology_lab:
		return
	
	# If company_address already set, skip
	if doc.company_address:
		return
	
	# Fetch lab_primary_address from Pathology Lab DocType
	primary_address = frappe.db.get_value("Pathology Lab", doc.pathology_lab, "lab_primary_address")
	
	if primary_address:
		doc.company_address = primary_address
	else:
		# Fallback: Find any billing address linked to this pathology lab
		address = frappe.db.sql("""
			SELECT a.name
			FROM `tabAddress` a
			INNER JOIN `tabDynamic Link` dl ON dl.parent = a.name
			WHERE dl.link_doctype = 'Pathology Lab'
			  AND dl.link_name = %s
			  AND a.disabled = 0
			  AND (a.is_primary_address = 1 OR a.address_type = 'Billing')
			ORDER BY a.is_primary_address DESC, a.creation DESC
			LIMIT 1
		""", doc.pathology_lab, as_dict=1)
		
		if address:
			doc.company_address = address[0].name

def set_address_gstin(doc):
	"""Fetch GSTIN from customer and company addresses"""
	if doc.customer_address and not doc.billing_address_gstin:
		doc.billing_address_gstin = frappe.db.get_value("Address", doc.customer_address, "gstin")
	
	if doc.company_address and not doc.company_gstin:
		doc.company_gstin = frappe.db.get_value("Address", doc.company_address, "gstin")

def set_place_of_supply(doc):
	"""Set place of supply from customer address GST state"""
	if not doc.customer_address:
		return
	
	if doc.place_of_supply:
		return
	
	# Get GST state and state number from customer address
	address_data = frappe.db.get_value(
		"Address", 
		doc.customer_address, 
		["gst_state", "gst_state_number"],
		as_dict=1
	)
	
	if address_data and address_data.gst_state_number and address_data.gst_state:
		# Format: "27-Maharashtra"
		doc.place_of_supply = f"{address_data.gst_state_number}-{address_data.gst_state}"

def compute_doctor_commission(doc):
	"""Calculate doctor commission"""
	if not doc.referred_by:
		return
	
	doctor = frappe.get_doc("Doctor", doc.referred_by)
	if doctor.commission_type == "None":
		return
	
	base_amount = doc.taxable_amount if doctor.commission_on == "Net" else doc.gross_amount
	
	if doctor.commission_type == "Percentage":
		doc.commission_amount = base_amount * doctor.commission_rate / 100
	elif doctor.commission_type == "Fixed Per Test":
		doc.commission_amount = len(doc.items) * doctor.commission_rate

def create_payment_link(doc):
	"""Create payment link using frappe/payments"""
	pass

def send_invoice_notification(doc):
	"""Send invoice notification"""
	pass

@frappe.whitelist()
def get_patient_gst_details(patient, pathology_lab):
	"""
	Fetch all GST-related details for instant population when patient is selected.
	Similar to india_compliance.gst_india.overrides.transaction.get_gst_details
	
	Returns dict with:
	- customer_address, billing_address_gstin, gst_category, place_of_supply
	- company_address, company_gstin
	- taxes_and_charges, taxes[]
	"""
	if not patient:
		return {}
	
	gst_details = frappe._dict()
	
	# Fetch patient primary address and contact
	patient_data = frappe.db.get_value(
		"Patient", 
		patient, 
		["patient_primary_address", "patient_primary_contact"],
		as_dict=1
	)
	
	if patient_data and patient_data.patient_primary_address:
		patient_primary_address = patient_data.patient_primary_address
		gst_details.customer_address = patient_primary_address
		
		# Set contact person if available
		if patient_data.patient_primary_contact:
			gst_details.contact_person = patient_data.patient_primary_contact
			# Fetch contact display, mobile, email
			contact_data = frappe.db.get_value(
				"Contact",
				patient_data.patient_primary_contact,
				["first_name", "last_name", "mobile_no", "email_id"],
				as_dict=1
			)
			if contact_data:
				contact_name = f"{contact_data.first_name or ''} {contact_data.last_name or ''}".strip()
				gst_details.contact_display = contact_name
				gst_details.contact_mobile = contact_data.mobile_no
				gst_details.contact_email = contact_data.email_id
		
		# Fetch GSTIN, state, and category from address
		address_data = frappe.db.get_value(
			"Address",
			patient_primary_address,
			["gstin", "gst_state", "gst_state_number", "gst_category"],
			as_dict=1
		)
		
		if address_data:
			gst_details.billing_address_gstin = address_data.gstin or ""
			gst_details.gst_category = address_data.gst_category or "Unregistered"
			
			# Set place of supply (format: "27-Maharashtra")
			if address_data.gst_state_number and address_data.gst_state:
				gst_details.place_of_supply = f"{address_data.gst_state_number}-{address_data.gst_state}"
	else:
		# Fallback: try to find any address linked to patient
		address = frappe.db.sql("""
			SELECT a.name, a.gstin, a.gst_state, a.gst_state_number, a.gst_category
			FROM `tabAddress` a
			INNER JOIN `tabDynamic Link` dl ON dl.parent = a.name
			WHERE dl.link_doctype = 'Patient'
			  AND dl.link_name = %s
			  AND a.disabled = 0
			  AND (a.is_primary_address = 1 OR a.address_type = 'Billing')
			ORDER BY a.is_primary_address DESC, a.creation DESC
			LIMIT 1
		""", patient, as_dict=1)
		
		if address:
			addr = address[0]
			gst_details.customer_address = addr.name
			gst_details.billing_address_gstin = addr.gstin or ""
			gst_details.gst_category = addr.gst_category or "Unregistered"
			if addr.gst_state_number and addr.gst_state:
				gst_details.place_of_supply = f"{addr.gst_state_number}-{addr.gst_state}"
	
	# Fetch pathology lab address, GSTIN, and contact
	if pathology_lab:
		lab_data = frappe.db.get_value(
			"Pathology Lab",
			pathology_lab,
			["lab_primary_address", "lab_primary_contact"],
			as_dict=1
		)
		
		if lab_data and lab_data.lab_primary_address:
			gst_details.company_address = lab_data.lab_primary_address
			company_gstin = frappe.db.get_value("Address", lab_data.lab_primary_address, "gstin")
			if company_gstin:
				gst_details.company_gstin = company_gstin
			
			# Set company contact person if available
			if lab_data.lab_primary_contact:
				gst_details.company_contact_person = lab_data.lab_primary_contact
		elif lab_data:
			# Fallback: try to find any address linked to pathology lab
			address = frappe.db.sql("""
				SELECT a.name, a.gstin
				FROM `tabAddress` a
				INNER JOIN `tabDynamic Link` dl ON dl.parent = a.name
				WHERE dl.link_doctype = 'Pathology Lab'
				  AND dl.link_name = %s
				  AND a.disabled = 0
				  AND (a.is_primary_address = 1 OR a.address_type = 'Billing')
				ORDER BY a.is_primary_address DESC, a.creation DESC
				LIMIT 1
			""", pathology_lab, as_dict=1)
			
			if address:
				gst_details.company_address = address[0].name
				gst_details.company_gstin = address[0].gstin or ""
			
			# Set company contact even if no address found
			if lab_data.lab_primary_contact:
				gst_details.company_contact_person = lab_data.lab_primary_contact
	
	# Auto-select tax template and tax category based on GST category and place of supply
	if gst_details.get("gst_category") and pathology_lab:
		# Determine tax category based on inter-state/intra-state
		tax_category = get_tax_category_for_transaction(
			gst_details.get("place_of_supply"),
			gst_details.get("company_gstin")
		)
		if tax_category:
			gst_details.tax_category = tax_category
		
		tax_template = get_tax_template_for_patient(
			gst_details.get("gst_category"),
			gst_details.get("place_of_supply"),
			gst_details.get("company_gstin"),
			pathology_lab
		)
		
		if tax_template:
			gst_details.taxes_and_charges = tax_template
			
			# Fetch tax rows from template
			tax_rows = frappe.get_all(
				"Lab Tax Row",
				filters={"parent": tax_template},
				fields=["charge_type", "account_head", "rate", "description", "gst_tax_type"],
				order_by="idx"
			)
			
			if tax_rows:
				gst_details.taxes = tax_rows
	
	return gst_details


def get_tax_template_for_patient(gst_category, place_of_supply, company_gstin, pathology_lab):
	"""
	Select appropriate tax template based on GST category and place of supply.
	Similar to india_compliance tax template selection logic.
	
	Returns: Tax template name or None
	"""
	# No tax for unregistered, overseas, or SEZ
	if not gst_category or gst_category in ["Unregistered", "Overseas", "SEZ"]:
		return None
	
	# Determine if inter-state or intra-state
	is_inter_state = False
	if place_of_supply and company_gstin and len(company_gstin) >= 2:
		company_state = company_gstin[:2]
		supply_state = place_of_supply.split("-")[0] if "-" in place_of_supply else ""
		is_inter_state = (company_state != supply_state)
	
	# Query Lab Tax Template based on inter-state/intra-state
	# Find the appropriate Lab Tax Category first
	tax_category_doc = frappe.db.get_value(
		"Lab Tax Category",
		{
			"disabled": 0,
			"is_inter_state": 1 if is_inter_state else 0,
			"is_reverse_charge": 0
		},
		"name"
	)
	
	if not tax_category_doc:
		# Fallback: find any template for this pathology lab
		return frappe.db.get_value(
			"Lab Tax Template",
			{"disabled": 0, "pathology_lab": pathology_lab},
			"name"
		)
	
	# Find template matching the tax category
	template = frappe.db.get_value(
		"Lab Tax Template",
		{
			"disabled": 0,
			"pathology_lab": pathology_lab,
			"tax_category": tax_category_doc
		},
		"name"
	)
	
	if not template:
		# Fallback: find any template for this pathology lab
		template = frappe.db.get_value(
			"Lab Tax Template",
			{"disabled": 0, "pathology_lab": pathology_lab},
			"name"
		)
	
	return template


def get_tax_category_for_transaction(place_of_supply, company_gstin):
	"""
	Determine appropriate tax category based on inter-state/intra-state.
	Returns: Lab Tax Category name or None
	"""
	if not place_of_supply or not company_gstin or len(company_gstin) < 2:
		return None
	
	# Determine if inter-state or intra-state
	company_state = company_gstin[:2]
	supply_state = place_of_supply.split("-")[0] if "-" in place_of_supply else ""
	is_inter_state = (company_state != supply_state)
	
	# Query Lab Tax Category
	filters = {
		"disabled": 0,
		"is_inter_state": 1 if is_inter_state else 0,
		"is_reverse_charge": 0  # Normal transactions, not RCM
	}
	
	tax_category = frappe.db.get_value("Lab Tax Category", filters, "name")
	return tax_category
