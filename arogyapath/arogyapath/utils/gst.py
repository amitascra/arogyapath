import re
import frappe

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
GST_RATE_STANDARD = 18.0
GST_RATE_EXEMPT = 0.0
DEFAULT_SAC_CODE = "999316"

GSTIN_PATTERN = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

# Matches India Compliance's STATE_NUMBERS — key: 2-digit code, value: state name
INDIA_STATE_CODES = {
	"01": "Jammu and Kashmir",
	"02": "Himachal Pradesh",
	"03": "Punjab",
	"04": "Chandigarh",
	"05": "Uttarakhand",
	"06": "Haryana",
	"07": "Delhi",
	"08": "Rajasthan",
	"09": "Uttar Pradesh",
	"10": "Bihar",
	"11": "Sikkim",
	"12": "Arunachal Pradesh",
	"13": "Nagaland",
	"14": "Manipur",
	"15": "Mizoram",
	"16": "Tripura",
	"17": "Meghalaya",
	"18": "Assam",
	"19": "West Bengal",
	"20": "Jharkhand",
	"21": "Odisha",
	"22": "Chhattisgarh",
	"23": "Madhya Pradesh",
	"24": "Gujarat",
	"25": "Daman and Diu",
	"26": "Dadra and Nagar Haveli and Daman and Diu",
	"27": "Maharashtra",
	"28": "Andhra Pradesh (Old)",
	"29": "Karnataka",
	"30": "Goa",
	"31": "Lakshadweep",
	"32": "Kerala",
	"33": "Tamil Nadu",
	"34": "Puducherry",
	"35": "Andaman and Nicobar Islands",
	"36": "Telangana",
	"37": "Andhra Pradesh",
	"38": "Ladakh",
	"97": "Other Territory",
	"99": "Centre Jurisdiction",
}

# GST categories that make a transaction exempt from GST on the sales side
GST_EXEMPT_CATEGORIES = {"Unregistered", "Overseas", "SEZ"}


# ─────────────────────────────────────────────────────────────────────────────
# GSTIN helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_state_code_from_gstin(gstin: str) -> str:
	"""Extract 2-digit state code from a GSTIN string."""
	if gstin and len(gstin) >= 2:
		return gstin[:2]
	return ""


def get_state_name(state_code: str) -> str:
	"""Return state name for a given 2-digit GST state code."""
	return INDIA_STATE_CODES.get(state_code, state_code)


def validate_gstin(gstin: str, label: str = "GSTIN") -> bool:
	"""Validate GSTIN format. Throws if invalid."""
	if not gstin:
		return True
	gstin = gstin.strip().upper()
	if not re.match(GSTIN_PATTERN, gstin):
		frappe.throw(
			f"Invalid {label} format: <b>{gstin}</b>. "
			"Expected 15-character format: 2 digits + 5 letters + 4 digits "
			"+ 1 letter + 1 alphanumeric + Z + 1 alphanumeric"
		)
	return True


def format_gstin(gstin: str) -> str:
	"""Return GSTIN in uppercase for display (used in Jinja templates)."""
	return (gstin or "").strip().upper()


# ─────────────────────────────────────────────────────────────────────────────
# Place of Supply
# ─────────────────────────────────────────────────────────────────────────────

def get_place_of_supply(invoice) -> str:
	"""
	Derive place of supply for a Lab Invoice.
	Priority:
	  1. billing_address_gstin (registered customer) → first 2 digits + state name
	  2. customer_address.gst_state_number + gst_state (unregistered with address)
	  3. company_gstin (fallback to lab state — intrastate)
	"""
	# Registered customer — GSTIN available via fetch_from
	customer_gstin = invoice.get("billing_address_gstin") or ""
	if customer_gstin and len(customer_gstin) >= 2:
		state_code = customer_gstin[:2]
		state_name = get_state_name(state_code)
		if state_name:
			return f"{state_code}-{state_name}"

	# Unregistered — try reading gst_state_number from linked Address
	customer_address = invoice.get("customer_address")
	if customer_address:
		gst_state_number, gst_state = frappe.db.get_value(
			"Address",
			customer_address,
			("gst_state_number", "gst_state"),
		) or ("", "")
		if gst_state_number and gst_state:
			return f"{gst_state_number}-{gst_state}"

	# Fallback: lab's own GSTIN state = intrastate
	company_gstin = invoice.get("company_gstin") or ""
	if company_gstin and len(company_gstin) >= 2:
		state_code = company_gstin[:2]
		state_name = get_state_name(state_code)
		if state_name:
			return f"{state_code}-{state_name}"

	return ""


def is_interstate(company_gstin: str, place_of_supply: str) -> bool:
	"""
	Return True if transaction is interstate (triggers IGST).
	Compares first 2 digits of company GSTIN vs place of supply state code.
	"""
	if not company_gstin or not place_of_supply:
		return False
	lab_state_code = company_gstin[:2]
	pos_state_code = place_of_supply[:2]
	return lab_state_code.strip() != pos_state_code.strip()


def get_place_of_supply_options() -> list:
	"""Return formatted list for Autocomplete field options."""
	return [f"{code}-{name}" for code, name in sorted(INDIA_STATE_CODES.items())]


# ─────────────────────────────────────────────────────────────────────────────
# Tax Template population (ERPNext/India Compliance pattern)
# ─────────────────────────────────────────────────────────────────────────────

def populate_taxes_from_template(invoice) -> None:
	"""
	Populate the taxes child table from the selected taxes_and_charges template.
	Mirrors ERPNext's get_taxes_and_charges() behaviour.
	Called from lab_invoice.py after taxes_and_charges is set.
	"""
	template_name = invoice.get("taxes_and_charges")
	if not template_name:
		invoice.taxes = []
		return

	template = frappe.get_cached_doc("Lab Tax Template", template_name)
	invoice.taxes = []
	for row in template.taxes:
		invoice.append("taxes", {
			"charge_type": row.charge_type,
			"account_head": row.account_head,
			"description": row.description,
			"rate": row.rate,
			"tax_amount": 0.0,
			"gst_tax_type": row.get("gst_tax_type") or "",
		})


def get_tax_template_for_invoice(invoice) -> str:
	"""
	Find the best matching Sales Taxes and Charges Template for this invoice.
	Priority:
	  1. Tax Category on invoice → template linked to that Tax Category + pathology_lab
	  2. Auto-detect via is_interstate + pathology_lab
	  3. Return "" (no template)

	This mirrors India Compliance's get_tax_template() logic, scoped to
	Pathology Lab instead of Company.
	"""
	pathology_lab = _get_pathology_lab_for_invoice(invoice)

	# 1. Use tax_category if set
	if invoice.get("tax_category"):
		template = frappe.db.get_value(
			"Lab Tax Template",
			{
				"tax_category": invoice.tax_category,
				"pathology_lab": pathology_lab,
				"disabled": 0,
			},
			"name",
		)
		if template:
			return template

	# 2. Auto-detect: resolve inter/intra state
	company_gstin = invoice.get("company_gstin") or ""
	pos = invoice.get("place_of_supply") or ""
	interstate_flag = is_interstate(company_gstin, pos)

	# Find matching Tax Category
	tax_categories = frappe.get_all(
		"Lab Tax Category",
		fields=["name", "is_inter_state", "gst_state"],
		filters={
			"is_inter_state": 1 if interstate_flag else 0,
			"is_reverse_charge": 0,
			"disabled": 0,
		},
	)

	for tc in tax_categories:
		# Prefer state-specific first, then generic
		tc_state_code = ""
		if tc.gst_state:
			# Find state code from state name
			for code, name in INDIA_STATE_CODES.items():
				if name == tc.gst_state:
					tc_state_code = code
					break

		if tc_state_code and company_gstin and tc_state_code != company_gstin[:2]:
			continue

		template = frappe.db.get_value(
			"Lab Tax Template",
			{
				"tax_category": tc.name,
				"pathology_lab": pathology_lab,
				"disabled": 0,
			},
			"name",
		)
		if template:
			return template

	return ""


def _get_pathology_lab_for_invoice(invoice) -> str:
	"""Resolve pathology_lab from branch linked to the invoice."""
	branch = invoice.get("branch")
	if not branch:
		return ""
	return frappe.db.get_value("Lab Branch", branch, "pathology_lab") or ""


# ─────────────────────────────────────────────────────────────────────────────
# GST Computation (item-level + header totals)
# ─────────────────────────────────────────────────────────────────────────────

def get_tax_rates(interstate_flag: bool) -> dict:
	"""Return CGST/SGST/IGST rates based on interstate flag."""
	if interstate_flag:
		return {"igst_rate": GST_RATE_STANDARD, "cgst_rate": 0.0, "sgst_rate": 0.0}
	half = GST_RATE_STANDARD / 2
	return {"igst_rate": 0.0, "cgst_rate": half, "sgst_rate": half}


def compute_invoice_taxes(invoice) -> None:
	"""
	Compute item-level GST and header totals for a Lab Invoice.

	Rules (matching India Compliance logic):
	  - gst_category fetched from customer_address via fetch_from
	  - Unregistered / Overseas / SEZ → all items exempt (Bill of Supply)
	  - Registered Regular / Composition → 18% GST per test (unless is_gst_exempt)
	  - Intrastate  → CGST (9%) + SGST (9%)
	  - Interstate  → IGST (18%)

	Header fields updated: gross_amount, total_discount, taxable_amount,
	                        total_cgst, total_sgst, total_igst, total_tax,
	                        grand_total, outstanding_amount
	"""
	# ── Determine interstate from Address-fetched GSTINs ──────────────────
	company_gstin = invoice.get("company_gstin") or ""
	pos = invoice.get("place_of_supply") or ""
	interstate_flag = is_interstate(company_gstin, pos)

	# ── GST category comes from customer_address via fetch_from ───────────
	# If the fetch hasn't happened yet (e.g. JS side), fall back to "Unregistered"
	gst_category = (invoice.get("gst_category") or "Unregistered").strip()
	exempt_invoice = gst_category in GST_EXEMPT_CATEGORIES

	rates = get_tax_rates(interstate_flag)

	gross = 0.0
	taxable = 0.0
	discount_total = 0.0
	cgst_total = sgst_total = igst_total = 0.0

	# Proportional discount ratio
	raw_gross = sum(flt(item.amount) for item in invoice.items) if invoice.items else 0.0
	discount_amount = flt(getattr(invoice, "discount_amount", 0))
	discount_ratio = (discount_amount / raw_gross) if (discount_amount and raw_gross) else 0.0

	for item in invoice.items:
		item_gross = flt(item.amount)
		gross += item_gross

		item_discount = flt(item_gross * discount_ratio, 2)
		item_taxable = flt(item_gross - item_discount, 2)
		discount_total += item_discount

		# Per-item exemption check (is_gst_exempt on Lab Test Master)
		is_exempt = exempt_invoice
		if not is_exempt and item.get("test"):
			test_exempt = frappe.db.get_value("Lab Test Master", item.test, "is_gst_exempt")
			is_exempt = bool(test_exempt)

		if is_exempt:
			item.cgst_rate = item.sgst_rate = item.igst_rate = 0.0
			item.cgst_amount = item.sgst_amount = item.igst_amount = 0.0
			item.tax_amount = 0.0
		else:
			item.cgst_rate = rates["cgst_rate"]
			item.sgst_rate = rates["sgst_rate"]
			item.igst_rate = rates["igst_rate"]
			item.cgst_amount = flt(item_taxable * rates["cgst_rate"] / 100, 2)
			item.sgst_amount = flt(item_taxable * rates["sgst_rate"] / 100, 2)
			item.igst_amount = flt(item_taxable * rates["igst_rate"] / 100, 2)
			# Set tax_amount field (sum of all GST components)
			item.tax_amount = flt(item.cgst_amount + item.sgst_amount + item.igst_amount, 2)

		# Set taxable_amount on item
		item.taxable_amount = item_taxable

		taxable += item_taxable
		cgst_total += item.cgst_amount
		sgst_total += item.sgst_amount
		igst_total += item.igst_amount

		# Ensure SAC code is set
		if not item.get("hsn_sac_code"):
			item.hsn_sac_code = DEFAULT_SAC_CODE

	# ── Header totals — using the correct field names ─────────────────────
	invoice.gross_amount = flt(gross, 2)
	invoice.total_discount = flt(discount_total, 2)
	invoice.taxable_amount = flt(taxable, 2)
	invoice.total_cgst = flt(cgst_total, 2)
	invoice.total_sgst = flt(sgst_total, 2)
	invoice.total_igst = flt(igst_total, 2)
	invoice.total_tax = flt(cgst_total + sgst_total + igst_total, 2)
	invoice.grand_total = flt(taxable + invoice.total_tax, 2)
	invoice.outstanding_amount = flt(
		invoice.grand_total - flt(getattr(invoice, "paid_amount", 0)), 2
	)


# ─────────────────────────────────────────────────────────────────────────────
# Doctor Commission
# ─────────────────────────────────────────────────────────────────────────────

def compute_doctor_commission(invoice) -> None:
	"""
	Compute doctor commission. Called from Lab Invoice validate.
	commission_on: Gross / Net (after discount)
	"""
	if not invoice.referred_by or not getattr(invoice, "commission_rate", 0):
		invoice.commission_amount = 0.0
		return

	base = (
		invoice.gross_amount
		if getattr(invoice, "commission_on", "Net") == "Gross"
		else invoice.taxable_amount
	)
	invoice.commission_amount = flt(base * flt(invoice.commission_rate) / 100, 2)


# ─────────────────────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────────────────────

def flt(value, precision: int = 2) -> float:
	"""Safe float rounding helper."""
	try:
		return round(float(value or 0), precision)
	except (TypeError, ValueError):
		return 0.0
