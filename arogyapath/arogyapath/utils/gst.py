import re
import frappe

GST_RATE_STANDARD = 18.0
GST_RATE_EXEMPT = 0.0
DEFAULT_SAC_CODE = "999316"

GSTIN_PATTERN = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

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
			"Expected 15-character format: 2 digits + 5 letters + 4 digits + 1 letter + 1 alphanumeric + Z + 1 alphanumeric"
		)
	return True


def format_gstin(gstin: str) -> str:
	"""Return GSTIN in uppercase for display."""
	return (gstin or "").strip().upper()


def is_interstate(lab_state_code: str, supply_state_code: str) -> bool:
	"""Return True if the supply is to a different state (triggers IGST)."""
	if not lab_state_code or not supply_state_code:
		return False
	return lab_state_code.strip() != supply_state_code.strip()


def get_tax_rates(is_interstate_flag: bool) -> dict:
	"""Return CGST/SGST/IGST rates based on interstate flag."""
	if is_interstate_flag:
		return {"igst_rate": GST_RATE_STANDARD, "cgst_rate": 0.0, "sgst_rate": 0.0}
	half = GST_RATE_STANDARD / 2
	return {"igst_rate": 0.0, "cgst_rate": half, "sgst_rate": half}


def compute_invoice_taxes(invoice) -> None:
	"""
	Compute item-level and header-level GST for a Lab Invoice document.

	Rules:
	- Individual patient (gst_category == "Unregistered") → all items exempt
	- Corporate/B2B (gst_category == "Registered") → apply GST per test flag
	- SEZ / Overseas → 0% (zero-rated / out of scope)
	- Intrastate → CGST + SGST (9% + 9%)
	- Interstate → IGST (18%)
	"""
	if not invoice.branch:
		return

	branch = frappe.get_cached_doc("Lab Branch", invoice.branch)
	lab_state = branch.state_code or ""
	supply_state = (invoice.place_of_supply or "").strip()

	interstate_flag = is_interstate(lab_state, supply_state)
	invoice.is_interstate = 1 if interstate_flag else 0

	# Determine if invoice is GST exempt based on supply_type
	# B2C (individual patients) = Unregistered = No GST
	# B2B (corporate) = Registered = 18% GST
	# SEZ/Export = No GST
	supply_type = getattr(invoice, 'supply_type', 'B2C')
	exempt_invoice = supply_type in ("B2C", "SEZ", "Export", None, "")
	rates = get_tax_rates(interstate_flag)

	gross = 0.0
	taxable = 0.0
	cgst_total = sgst_total = igst_total = 0.0

	# Proportional discount ratio for distributing invoice-level discount to items
	raw_gross = sum(item.amount for item in invoice.items) if invoice.items else 0.0
	discount_ratio = 0.0
	if invoice.discount_amount and raw_gross:
		discount_ratio = float(invoice.discount_amount) / raw_gross

	for item in invoice.items:
		item_gross = flt(item.amount)
		gross += item_gross

		# Apply proportional discount to item
		item_discount = flt(item_gross * discount_ratio, 2)
		item_taxable = flt(item_gross - item_discount, 2)

		# Determine if item is GST exempt
		is_exempt = exempt_invoice
		if not is_exempt and item.test:
			test_exempt = frappe.db.get_value("Lab Test Master", item.test, "is_gst_exempt")
			is_exempt = bool(test_exempt)

		if is_exempt:
			item.cgst_rate = item.sgst_rate = item.igst_rate = 0.0
			item.cgst_amount = item.sgst_amount = item.igst_amount = 0.0
		else:
			item.cgst_rate = rates["cgst_rate"]
			item.sgst_rate = rates["sgst_rate"]
			item.igst_rate = rates["igst_rate"]
			item.cgst_amount = flt(item_taxable * rates["cgst_rate"] / 100, 2)
			item.sgst_amount = flt(item_taxable * rates["sgst_rate"] / 100, 2)
			item.igst_amount = flt(item_taxable * rates["igst_rate"] / 100, 2)

		taxable += item_taxable
		cgst_total += item.cgst_amount
		sgst_total += item.sgst_amount
		igst_total += item.igst_amount

		# Ensure SAC code is set
		if not item.hsn_sac_code:
			item.hsn_sac_code = DEFAULT_SAC_CODE

	invoice.gross_amount = flt(gross, 2)
	invoice.taxable_amount = flt(taxable, 2)
	invoice.cgst_amount = flt(cgst_total, 2)
	invoice.sgst_amount = flt(sgst_total, 2)
	invoice.igst_amount = flt(igst_total, 2)
	invoice.total_tax = flt(cgst_total + sgst_total + igst_total, 2)
	invoice.grand_total = flt(taxable + invoice.total_tax, 2)
	invoice.outstanding_amount = flt(invoice.grand_total - flt(invoice.paid_amount), 2)


def compute_doctor_commission(invoice) -> None:
	"""
	Compute doctor commission on invoice. Called from Lab Invoice validate.
	commission_on: Gross / Net (after discount)
	"""
	if not invoice.referred_by or not invoice.commission_rate:
		invoice.commission_amount = 0.0
		return

	base = invoice.gross_amount if invoice.commission_on == "Gross" else invoice.taxable_amount
	invoice.commission_amount = flt(base * flt(invoice.commission_rate) / 100, 2)


def get_place_of_supply_options() -> list:
	"""Return list of state code + name tuples for Select field options."""
	return [f"{code}-{name}" for code, name in sorted(INDIA_STATE_CODES.items())]


def flt(value, precision: int = 2) -> float:
	"""Safe float rounding helper."""
	try:
		return round(float(value or 0), precision)
	except (TypeError, ValueError):
		return 0.0
