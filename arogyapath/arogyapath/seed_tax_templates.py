# Copyright (c) 2026, Ascratech and contributors
# Seed GST Tax Categories and Sales/Purchase Tax Templates
#
# Pattern mirrors India Compliance:
#   - ERPNext Tax Category is extended with is_inter_state / is_reverse_charge
#     / gst_state via custom fields (see utils/custom_fields.py)
#   - Sales Taxes and Charges Template is extended with pathology_lab +
#     tax_category custom fields
#   - Each pathology lab gets its own templates linked by pathology_lab field
#
# All functions are idempotent — safe to call on every bench migrate.

import frappe


# ─────────────────────────────────────────────────────────────────────────────
# Tax Categories  (ERPNext core DocType, extended via custom fields)
# ─────────────────────────────────────────────────────────────────────────────

GST_TAX_CATEGORIES = [
	{
		"name": "In State GST",
		"is_inter_state": 0,
		"is_reverse_charge": 0,
	},
	{
		"name": "Out of State GST",
		"is_inter_state": 1,
		"is_reverse_charge": 0,
	},
	{
		"name": "In State GST RCM",
		"is_inter_state": 0,
		"is_reverse_charge": 1,
	},
	{
		"name": "Out of State GST RCM",
		"is_inter_state": 1,
		"is_reverse_charge": 1,
	},
]


def seed_gst_tax_categories():
	"""Seed Lab Tax Category records (our own DocType, not ERPNext's Tax Category)."""
	inserted = 0
	for tc in GST_TAX_CATEGORIES:
		if frappe.db.exists("Lab Tax Category", tc["name"]):
			frappe.db.set_value(
				"Lab Tax Category", tc["name"],
				{
					"is_inter_state": tc["is_inter_state"],
					"is_reverse_charge": tc["is_reverse_charge"],
					"disabled": 0,
				},
			)
		else:
			doc = frappe.new_doc("Lab Tax Category")
			doc.category_name = tc["name"]
			doc.is_inter_state = tc["is_inter_state"]
			doc.is_reverse_charge = tc["is_reverse_charge"]
			doc.disabled = 0
			doc.insert(ignore_permissions=True)
			inserted += 1

	if inserted:
		frappe.logger().info(f"ArogyaPath: Seeded {inserted} Lab Tax Categories")


# ─────────────────────────────────────────────────────────────────────────────
# Sales Taxes and Charges Templates  (per Pathology Lab)
# ─────────────────────────────────────────────────────────────────────────────

def _get_gst_accounts(pathology_lab: str) -> dict:
	"""
	Return GST output account names for the given pathology lab.
	Looks up accounts from the chart of accounts seeded by seed_chart_of_accounts.py.
	Falls back to generic names if not found.
	"""
	def _find_account(suffix):
		account = frappe.db.get_value(
			"Account",
			{"account_name": ["like", f"%{suffix}%"], "company": pathology_lab},
			"name",
		)
		return account or suffix  # fallback to suffix as-is

	return {
		"cgst": _find_account("Output Tax CGST"),
		"sgst": _find_account("Output Tax SGST"),
		"igst": _find_account("Output Tax IGST"),
	}


def seed_sales_tax_templates_for_lab(pathology_lab: str):
	"""
	Seed the two mandatory Sales Taxes and Charges Templates for a lab:
	  1. GST 18% Intrastate  → linked to "In State GST" Tax Category
	  2. GST 18% Interstate  → linked to "Out of State GST" Tax Category

	Uses pathology_lab custom field to scope templates per lab.
	Idempotent — skips if already present.
	"""
	accounts = _get_gst_accounts(pathology_lab)

	templates = [
		{
			"title": f"GST 18% Intrastate - {pathology_lab}",
			"tax_category": "In State GST",
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": accounts["cgst"],
					"description": "CGST @ 9%",
					"rate": 9.0,
					"gst_tax_type": "cgst",
				},
				{
					"charge_type": "On Net Total",
					"account_head": accounts["sgst"],
					"description": "SGST @ 9%",
					"rate": 9.0,
					"gst_tax_type": "sgst",
				},
			],
		},
		{
			"title": f"GST 18% Interstate - {pathology_lab}",
			"tax_category": "Out of State GST",
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": accounts["igst"],
					"description": "IGST @ 18%",
					"rate": 18.0,
					"gst_tax_type": "igst",
				},
			],
		},
	]

	inserted = 0
	for tmpl_data in templates:
		if frappe.db.exists("Lab Tax Template", tmpl_data["title"]):
			# Ensure pathology_lab and tax_category are set on existing records
			frappe.db.set_value(
				"Lab Tax Template",
				tmpl_data["title"],
				{
					"pathology_lab": pathology_lab,
					"tax_category": tmpl_data["tax_category"],
					"disabled": 0,
				},
			)
			continue

		tmpl = frappe.new_doc("Lab Tax Template")
		tmpl.title = tmpl_data["title"]
		tmpl.disabled = 0

		for tax_row in tmpl_data["taxes"]:
			tmpl.append("taxes", tax_row)

		tmpl.insert(ignore_permissions=True)

		# Set custom fields post-insert
		frappe.db.set_value(
			"Lab Tax Template",
			tmpl.name,
			{
				"pathology_lab": pathology_lab,
				"tax_category": tmpl_data["tax_category"],
			},
		)
		inserted += 1

	if inserted:
		frappe.logger().info(
			f"ArogyaPath: Seeded {inserted} Sales Tax Templates for lab '{pathology_lab}'"
		)


def seed_sales_tax_templates():
	"""
	Seed Sales Tax Templates for all existing Pathology Labs.
	Called from after_migrate in install.py.
	"""
	labs = frappe.get_all("Pathology Lab", pluck="name")
	for lab in labs:
		seed_sales_tax_templates_for_lab(lab)


# ─────────────────────────────────────────────────────────────────────────────
# Purchase Tax Templates  (standard ERPNext — no pathology_lab scoping needed)
# ─────────────────────────────────────────────────────────────────────────────

def seed_purchase_tax_templates():
	"""Seed standard Input GST Purchase Tax Templates (not lab-scoped)."""
	templates = [
		{
			"title": "Input GST 18% Intrastate",
			"taxes": [
				{"charge_type": "On Net Total", "account_head": "Input Tax CGST",
				 "description": "Input CGST @ 9%", "rate": 9.0, "gst_tax_type": "cgst"},
				{"charge_type": "On Net Total", "account_head": "Input Tax SGST",
				 "description": "Input SGST @ 9%", "rate": 9.0, "gst_tax_type": "sgst"},
			],
		},
		{
			"title": "Input GST 18% Interstate",
			"taxes": [
				{"charge_type": "On Net Total", "account_head": "Input Tax IGST",
				 "description": "Input IGST @ 18%", "rate": 18.0, "gst_tax_type": "igst"},
			],
		},
	]

	inserted = 0
	for tmpl_data in templates:
		if frappe.db.exists("Purchase Taxes and Charges Template", tmpl_data["title"]):
			continue

		tmpl = frappe.new_doc("Purchase Taxes and Charges Template")
		tmpl.title = tmpl_data["title"]
		for tax_row in tmpl_data["taxes"]:
			tmpl.append("taxes", tax_row)
		tmpl.insert(ignore_permissions=True)
		inserted += 1

	if inserted:
		frappe.logger().info(f"ArogyaPath: Seeded {inserted} Purchase Tax Templates")


# ─────────────────────────────────────────────────────────────────────────────
# TDS / Tax Withholding Categories
# ─────────────────────────────────────────────────────────────────────────────

def seed_tax_withholding_categories():
	"""Seed common TDS categories as per Indian Income Tax Act."""
	categories = [
		{"category_name": "194C - Contractor", "description": "Payment to contractors. TDS @ 1%"},
		{"category_name": "194J - Professional Services", "description": "Fees for professional services. TDS @ 10%"},
		{"category_name": "194H - Commission", "description": "Commission or brokerage. TDS @ 5%"},
		{"category_name": "194I - Rent", "description": "Rent for land/building. TDS @ 10%"},
		{"category_name": "194Q - Purchase of Goods", "description": "Purchase > Rs.50L. TDS @ 0.1%"},
	]

	inserted = 0
	for cat_data in categories:
		if not frappe.db.exists("Tax Withholding Category", cat_data["category_name"]):
			cat = frappe.new_doc("Tax Withholding Category")
			cat.category_name = cat_data["category_name"]
			cat.insert(ignore_permissions=True)
			inserted += 1

	if inserted:
		frappe.logger().info(f"ArogyaPath: Seeded {inserted} Tax Withholding Categories")
