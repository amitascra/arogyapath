# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt
#
# Address override — mirrors India Compliance's address.py
# Validates GSTIN, sets gst_state / gst_state_number from state,
# auto-derives gst_category from GSTIN prefix.

import re

import frappe
from frappe import _

# ── State lookup tables (name → code and code → name) ─────────────────────────
STATE_NUMBERS = {
	"Andaman and Nicobar Islands": "35",
	"Andhra Pradesh": "37",
	"Arunachal Pradesh": "12",
	"Assam": "18",
	"Bihar": "10",
	"Chandigarh": "04",
	"Chhattisgarh": "22",
	"Dadra and Nagar Haveli and Daman and Diu": "26",
	"Delhi": "07",
	"Goa": "30",
	"Gujarat": "24",
	"Haryana": "06",
	"Himachal Pradesh": "02",
	"Jammu and Kashmir": "01",
	"Jharkhand": "20",
	"Karnataka": "29",
	"Kerala": "32",
	"Ladakh": "38",
	"Lakshadweep Islands": "31",
	"Madhya Pradesh": "23",
	"Maharashtra": "27",
	"Manipur": "14",
	"Meghalaya": "17",
	"Mizoram": "15",
	"Nagaland": "13",
	"Odisha": "21",
	"Other Countries": "96",
	"Other Territory": "97",
	"Puducherry": "34",
	"Punjab": "03",
	"Rajasthan": "08",
	"Sikkim": "11",
	"Tamil Nadu": "33",
	"Telangana": "36",
	"Tripura": "16",
	"Uttar Pradesh": "09",
	"Uttarakhand": "05",
	"West Bengal": "19",
}

# ── GSTIN format regexes per GST category ─────────────────────────────────────
# Standard GSTIN: 2-digit state + 10-char PAN + 1 entity + Z + 1 check
GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")
# TDS/TCS: state + 4 digits + D/C + numeric + Z + check
TDS_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{4}[0-9]{5}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")
# Unique Common Enrolment (transporters): starts with 88
UIN_PATTERN = re.compile(r"^88[0-9A-Z]{13}$")
# SEZ unit
SEZ_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

GST_CATEGORY_OPTIONS = {
	"Registered Regular": GSTIN_PATTERN,
	"Registered Composition": GSTIN_PATTERN,
	"SEZ": SEZ_PATTERN,
	"Overseas": None,
	"Unregistered": None,
	"Deemed Export": GSTIN_PATTERN,
}

# Check-digit multiplier map (Luhn-variant used by GST)
_GSTIN_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _gstin_check_digit(gstin: str) -> str:
	"""Compute the expected GST check digit (last character)."""
	total = 0
	for i, ch in enumerate(gstin[:14]):
		val = _GSTIN_CHARS.index(ch)
		if i % 2 != 0:
			val = val * 2
		total += val // len(_GSTIN_CHARS) + val % len(_GSTIN_CHARS)
	check = (len(_GSTIN_CHARS) - total % len(_GSTIN_CHARS)) % len(_GSTIN_CHARS)
	return _GSTIN_CHARS[check]


def validate_gstin_format(gstin: str, label: str = "GSTIN") -> str:
	"""Validate GSTIN length, pattern and check digit. Returns normalised GSTIN."""
	if not gstin:
		return gstin

	gstin = gstin.strip().upper()

	if len(gstin) != 15:
		frappe.throw(
			_("{0} {1} must be exactly 15 characters").format(label, frappe.bold(gstin)),
			title=_("Invalid {0}").format(label),
		)

	if not GSTIN_PATTERN.match(gstin) and not TDS_PATTERN.match(gstin):
		frappe.throw(
			_("{0} {1} does not match the required format").format(label, frappe.bold(gstin)),
			title=_("Invalid {0}").format(label),
		)

	expected = _gstin_check_digit(gstin)
	if gstin[-1] != expected:
		frappe.throw(
			_(
				"{0} {1} has an invalid check digit. "
				"Please verify that you have entered it correctly."
			).format(label, frappe.bold(gstin)),
			title=_("Invalid {0}").format(label),
		)

	return gstin


def guess_gst_category(gstin: str, country: str = "India") -> str:
	"""
	Derive GST Category from GSTIN and country.
	Matches India Compliance's guess_gst_category() logic.
	"""
	if country and country != "India":
		return "Overseas"

	if not gstin:
		return "Unregistered"

	gstin = gstin.strip().upper()

	# UIN / embassy
	if UIN_PATTERN.match(gstin):
		return "UIN Holders"

	# TDS/TCS: PAN position 6 is 'C'
	if len(gstin) >= 12 and gstin[5] == "C":
		return "Tax Deductor"

	# Government department: PAN 6th char is 'G'
	if len(gstin) >= 12 and gstin[5] == "G":
		return "Registered Regular"

	return "Registered Regular"


def validate_gst_category(gst_category: str, gstin: str) -> None:
	"""Validate consistency between GST Category and GSTIN."""
	if not gst_category:
		return

	if not gstin:
		if gst_category not in ("Unregistered", "Overseas"):
			frappe.throw(
				_("GST Category should be Unregistered or Overseas when GSTIN is not provided"),
				title=_("Invalid GST Category"),
			)
		return

	if gst_category == "Unregistered":
		frappe.throw(
			_("GST Category cannot be Unregistered for an address with GSTIN"),
			title=_("Invalid GST Category"),
		)

	pattern = GST_CATEGORY_OPTIONS.get(gst_category)
	if pattern and not pattern.match(gstin):
		frappe.throw(
			_(
				"GSTIN {0} does not match the expected format for GST Category {1}."
			).format(frappe.bold(gstin), frappe.bold(gst_category)),
			title=_("Invalid GSTIN or GST Category"),
		)


def validate_state(doc) -> None:
	"""
	Set gst_state and gst_state_number from doc.state.
	Cross-validates GSTIN prefix against state number.
	Mirrors India Compliance's validate_state().
	"""
	country = doc.get("country") or "India"

	if country != "India":
		doc.gst_state = None
		doc.gst_state_number = None
		return

	state = doc.get("state") or ""

	if not state:
		# Non-fatal for non-GST addresses; only warn if GSTIN is set
		if doc.get("gstin"):
			frappe.throw(
				_("State is required for an Indian address with GSTIN"),
				title=_("Missing Mandatory Field"),
			)
		return

	if state not in STATE_NUMBERS:
		frappe.msgprint(
			_("State <b>{0}</b> is not a recognised GST state. "
			  "gst_state and gst_state_number will not be set.").format(state),
			indicator="orange",
			alert=True,
		)
		return

	doc.gst_state = state
	doc.gst_state_number = STATE_NUMBERS[state]

	# Cross-validate GSTIN prefix
	if doc.get("gstin") and len(doc.gstin) >= 2:
		if doc.gst_state_number != doc.gstin[:2]:
			frappe.throw(
				_(
					"First 2 digits of GSTIN should match the State Number for "
					"{0} ({1}). Got <b>{2}</b> in GSTIN."
				).format(
					frappe.bold(doc.gst_state),
					doc.gst_state_number,
					doc.gstin[:2],
				),
				title=_("Invalid GSTIN or State"),
			)


def set_gst_category(doc) -> None:
	"""Auto-derive gst_category from GSTIN if not already set to a non-default."""
	country = doc.get("country") or "India"
	guessed = guess_gst_category(doc.get("gstin") or "", country)

	current = doc.get("gst_category") or "Unregistered"

	# If already set to a meaningful specific value, don't overwrite
	if current in ("SEZ", "Overseas", "Deemed Export", "Registered Composition"):
		return

	if current != guessed:
		doc.gst_category = guessed
		frappe.msgprint(
			_("GST Category updated to {0}.").format(frappe.bold(guessed)),
			indicator="green",
			alert=True,
		)


# ── Main validate hook (called from doc_events) ────────────────────────────────

def validate(doc, method=None):
	"""
	Main validate hook for Address DocType.
	Wired via hooks.py doc_events.
	"""
	doc.gstin = validate_gstin_format(doc.get("gstin") or "")
	set_gst_category(doc)
	validate_gst_category(doc.get("gst_category"), doc.get("gstin"))
	validate_state(doc)


# ── Whitelisted API — called from address.js status indicator ──────────────────

@frappe.whitelist(allow_guest=False)
def get_gstin_status(gstin: str) -> dict:
	"""
	Return basic GSTIN status for the frontend indicator.
	Checks if GSTIN passes format validation; does NOT call GST portal API
	(no API credentials assumed). Returns:
	  { "status": "Active" | "Invalid Format" | "Not Available" }
	"""
	if not gstin:
		return {"status": "Not Available"}

	gstin = gstin.strip().upper()

	# Format check
	if len(gstin) != 15:
		return {"status": "Invalid Format"}

	if not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", gstin):
		# Also check TDS pattern
		if not re.match(r"^[0-9]{2}[A-Z]{4}[0-9]{5}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", gstin):
			return {"status": "Invalid Format"}

	# Check-digit
	chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	total = 0
	for i, ch in enumerate(gstin[:14]):
		if ch not in chars:
			return {"status": "Invalid Format"}
		val = chars.index(ch)
		if i % 2 != 0:
			val = val * 2
		total += val // len(chars) + val % len(chars)
	expected = chars[(len(chars) - total % len(chars)) % len(chars)]
	if gstin[-1] != expected:
		return {"status": "Invalid Format"}

	# Optionally check if this GSTIN has been saved on any Address in our system
	exists_in_system = frappe.db.exists("Address", {"gstin": gstin})
	return {"status": "Active" if exists_in_system else "Not Available"}
