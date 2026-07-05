# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt
#
# Pattern: identical to India Compliance's approach.
# - Define CUSTOM_FIELDS dict keyed by DocType (or tuple of DocTypes)
# - Call setup_custom_fields() from after_install and after_migrate
# - Frappe's create_custom_fields() is idempotent: creates OR updates existing fields

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

# ─────────────────────────────────────────────────────────────────────────────
# State options for Select fields — matches India Compliance STATE_NUMBERS
# ─────────────────────────────────────────────────────────────────────────────
INDIA_STATES = [
	"Andaman and Nicobar Islands",
	"Andhra Pradesh",
	"Arunachal Pradesh",
	"Assam",
	"Bihar",
	"Chandigarh",
	"Chhattisgarh",
	"Dadra and Nagar Haveli and Daman and Diu",
	"Delhi",
	"Goa",
	"Gujarat",
	"Haryana",
	"Himachal Pradesh",
	"Jammu and Kashmir",
	"Jharkhand",
	"Karnataka",
	"Kerala",
	"Ladakh",
	"Lakshadweep Islands",
	"Other Territory",
	"Madhya Pradesh",
	"Maharashtra",
	"Manipur",
	"Meghalaya",
	"Mizoram",
	"Nagaland",
	"Odisha",
	"Puducherry",
	"Punjab",
	"Rajasthan",
	"Sikkim",
	"Tamil Nadu",
	"Telangana",
	"Tripura",
	"Uttar Pradesh",
	"Uttarakhand",
	"West Bengal",
]

GST_STATE_OPTIONS = "\n" + "\n".join(INDIA_STATES)

GST_CATEGORY_OPTIONS = (
	"Unregistered\n"
	"Registered Regular\n"
	"Registered Composition\n"
	"SEZ\n"
	"Overseas\n"
	"Deemed Export"
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM_FIELDS
# Keys: DocType name (str) or tuple of DocType names
# Values: list of field dicts — same format as India Compliance
# ─────────────────────────────────────────────────────────────────────────────
CUSTOM_FIELDS = {
	# ── Address ──────────────────────────────────────────────────────────────
	# Core of the GST system. GSTIN + category live here, not on Party.
	# Sales Invoice (and Lab Invoice) fetch GSTIN/category from linked Address.
	"Address": [
		{
			"fieldname": "ap_tax_details_section",
			"label": "Tax Details",
			"fieldtype": "Section Break",
			"insert_after": "disabled",
			"module": "ArogyaPath",
		},
		{
			"fieldname": "gstin",
			"label": "GSTIN / UIN",
			"fieldtype": "Data",
			"insert_after": "ap_tax_details_section",
			"length": 15,
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "gst_state",
			"label": "GST State",
			"fieldtype": "Select",
			"options": GST_STATE_OPTIONS,
			"insert_after": "gstin",
			"read_only": 1,
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "ap_tax_col_break",
			"fieldtype": "Column Break",
			"insert_after": "gst_state",
			"module": "ArogyaPath",
		},
		{
			"fieldname": "gst_category",
			"label": "GST Category",
			"fieldtype": "Select",
			"options": GST_CATEGORY_OPTIONS,
			"default": "Unregistered",
			"insert_after": "ap_tax_col_break",
			"reqd": 1,
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "gst_state_number",
			"label": "GST State Number",
			"fieldtype": "Data",
			"insert_after": "gst_category",
			"read_only": 1,
			"translatable": 0,
			"module": "ArogyaPath",
		},
	],

	# ── Patient ───────────────────────────────────────────────────────────────
	# Plays the "Customer" role. Link to Address for GST — do NOT store GSTIN here.
	"Patient": [
		{
			"fieldname": "ap_address_section",
			"label": "Address & GST",
			"fieldtype": "Section Break",
			"insert_after": "email",
			"module": "ArogyaPath",
		},
		{
			"fieldname": "customer_primary_address",
			"label": "Primary Address",
			"fieldtype": "Link",
			"options": "Address",
			"insert_after": "ap_address_section",
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "primary_address",
			"label": "Primary Address Display",
			"fieldtype": "Text",
			"insert_after": "customer_primary_address",
			"read_only": 1,
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "ap_addr_col_break",
			"fieldtype": "Column Break",
			"insert_after": "primary_address",
			"module": "ArogyaPath",
		},
		{
			"fieldname": "pan",
			"label": "PAN",
			"fieldtype": "Data",
			"insert_after": "ap_addr_col_break",
			"length": 10,
			"translatable": 0,
			"module": "ArogyaPath",
		},
	],

	# ── Corporate Account ─────────────────────────────────────────────────────
	# B2B party. Link to Address for GST.
	"Corporate Account": [
		{
			"fieldname": "ap_corp_address_section",
			"label": "Address & GST",
			"fieldtype": "Section Break",
			"insert_after": "gstin",
			"module": "ArogyaPath",
		},
		{
			"fieldname": "primary_address",
			"label": "Primary Address",
			"fieldtype": "Link",
			"options": "Address",
			"insert_after": "ap_corp_address_section",
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "billing_address_display",
			"label": "Billing Address Display",
			"fieldtype": "Text",
			"insert_after": "primary_address",
			"read_only": 1,
			"translatable": 0,
			"module": "ArogyaPath",
		},
		{
			"fieldname": "ap_corp_col_break",
			"fieldtype": "Column Break",
			"insert_after": "billing_address_display",
			"module": "ArogyaPath",
		},
		{
			"fieldname": "pan",
			"label": "PAN",
			"fieldtype": "Data",
			"insert_after": "ap_corp_col_break",
			"length": 10,
			"translatable": 0,
			"module": "ArogyaPath",
		},
	],

	# ── Lab Branch ────────────────────────────────────────────────────────────
	# Add branch_address Link to Address — gstin is already native on Lab Branch.
	"Lab Branch": [
		{
			"fieldname": "branch_address",
			"label": "Branch Address",
			"fieldtype": "Link",
			"options": "Address",
			"insert_after": "nabl_number",
			"translatable": 0,
			"module": "ArogyaPath",
		},
	],

	# ── Pathology Lab ─────────────────────────────────────────────────────────
	# gstin is already native. Add company_address Link to Address.
	"Pathology Lab": [
		{
			"fieldname": "company_address",
			"label": "Registered Address",
			"fieldtype": "Link",
			"options": "Address",
			"insert_after": "gstin",
			"translatable": 0,
			"module": "ArogyaPath",
		},
	],

}


def setup_custom_fields():
	"""
	Called from after_install and after_migrate.
	Creates or updates all ArogyaPath GST custom fields.
	Idempotent — safe to run multiple times.
	"""
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.logger().info("ArogyaPath: GST custom fields created/updated.")
