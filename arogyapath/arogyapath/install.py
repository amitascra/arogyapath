import frappe
from frappe import _


def after_install():
	"""Run after app installation — creates roles, role profiles, and custom fields"""
	create_custom_roles()
	create_default_role_profiles()
	# Create GST custom fields (India Compliance pattern)
	from arogyapath.arogyapath.utils.custom_fields import setup_custom_fields
	setup_custom_fields()
	frappe.db.commit()


def after_migrate():
	"""Run after migration — DocTypes are fully synced, safe to insert demo data"""
	# Re-create/update GST custom fields on every migration (India Compliance pattern)
	from arogyapath.arogyapath.utils.custom_fields import setup_custom_fields
	setup_custom_fields()
	create_default_lab_settings()
	seed_lab_test_uom()
	# Phase 9 — Test Catalog seed (idempotent)
	from arogyapath.arogyapath.seed_catalog import (
		seed_lab_departments,
		seed_sample_types,
		seed_lab_tests,
		seed_lab_test_panels,
	)
	seed_lab_departments()
	seed_sample_types()
	seed_lab_tests()
	seed_lab_test_panels()
	# Phase 10D — Tax Categories + Templates seed (idempotent)
	# seed_gst_tax_categories must run AFTER setup_custom_fields so that
	# is_inter_state / is_reverse_charge columns exist on Tax Category
	from arogyapath.arogyapath.seed_tax_templates import (
		seed_gst_tax_categories,
		seed_tax_withholding_categories,
		seed_sales_tax_templates,
		seed_purchase_tax_templates,
	)
	seed_gst_tax_categories()
	seed_tax_withholding_categories()
	seed_sales_tax_templates()
	seed_purchase_tax_templates()
	# Phase 10G — Chart of Accounts seed (idempotent)
	from arogyapath.arogyapath.seed_chart_of_accounts import seed_chart_of_accounts
	seed_chart_of_accounts()
	frappe.db.commit()


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

ROLES = [
	{
		"role_name": "Lab Admin",
		"desk_access": 1,
		"is_custom": 1,
		"home_page": "/app/arogyapath",
	},
	{
		"role_name": "Lab Manager",
		"desk_access": 1,
		"is_custom": 1,
		"home_page": "/app/arogyapath",
	},
	{
		"role_name": "Lab Pathologist",
		"desk_access": 1,
		"is_custom": 1,
		"home_page": "/app/arogyapath",
	},
	{
		"role_name": "Lab Technician",
		"desk_access": 1,
		"is_custom": 1,
		"home_page": "/app/arogyapath",
	},
	{
		"role_name": "Lab Reception",
		"desk_access": 1,
		"is_custom": 1,
		"home_page": "/app/arogyapath",
	},
	{
		"role_name": "Lab Patient",
		"desk_access": 0,
		"is_custom": 1,
		"home_page": "/",
	},
]


def create_custom_roles():
	"""Create ArogyaPath custom roles — Frappe/ERPNext pattern"""
	for role_data in ROLES:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.get_doc({"doctype": "Role", **role_data})
			role.insert(ignore_permissions=True)
			frappe.logger().info(f"ArogyaPath: Created role '{role_data['role_name']}'")
		else:
			frappe.logger().info(f"ArogyaPath: Role '{role_data['role_name']}' already exists")


# ---------------------------------------------------------------------------
# Role Profiles
# ---------------------------------------------------------------------------

ROLE_PROFILES = {
	"Lab Admin Profile": [
		"Lab Admin",
		"Lab Manager",
		"Lab Pathologist",
		"Lab Technician",
		"Lab Reception",
	],
	"Lab Manager Profile": [
		"Lab Manager",
		"Lab Technician",
		"Lab Reception",
	],
	"Lab Pathologist Profile": [
		"Lab Pathologist",
	],
	"Lab Technician Profile": [
		"Lab Technician",
	],
	"Lab Receptionist Profile": [
		"Lab Reception",
	],
}


def create_default_role_profiles():
	"""Create ArogyaPath Role Profiles — Frappe/ERPNext pattern"""
	for profile_name, roles in ROLE_PROFILES.items():
		if frappe.db.exists("Role Profile", profile_name):
			rp = frappe.get_doc("Role Profile", profile_name)
			existing = [r.role for r in rp.roles]
			for role in roles:
				if role not in existing:
					rp.append("roles", {"role": role})
			rp.save(ignore_permissions=True)
			frappe.logger().info(f"ArogyaPath: Updated role profile '{profile_name}'")
		else:
			rp = frappe.new_doc("Role Profile")
			rp.role_profile = profile_name
			for role in roles:
				rp.append("roles", {"role": role})
			rp.insert(ignore_permissions=True)
			frappe.logger().info(f"ArogyaPath: Created role profile '{profile_name}'")


# ---------------------------------------------------------------------------
# Default Lab Settings (runs after_migrate so DocType table exists)
# ---------------------------------------------------------------------------

def create_default_lab_settings():
	"""Create a default Lab Settings singleton if not already set"""
	try:
		if not frappe.db.exists("Lab Settings", "Lab Settings"):
			settings = frappe.new_doc("Lab Settings")
			settings.insert(ignore_permissions=True)
			frappe.logger().info("ArogyaPath: Created default Lab Settings")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: Lab Settings creation failed")


# ---------------------------------------------------------------------------
# Lab Test UOM Master Seed Data
# ---------------------------------------------------------------------------

LAB_TEST_UOMS = [
	# Concentration
	{"uom_name": "g/dL", "uom_symbol": "g/dL", "uom_category": "Concentration", "description": "Grams per decilitre"},
	{"uom_name": "mg/dL", "uom_symbol": "mg/dL", "uom_category": "Concentration", "description": "Milligrams per decilitre"},
	{"uom_name": "µg/dL", "uom_symbol": "µg/dL", "uom_category": "Concentration", "description": "Micrograms per decilitre"},
	{"uom_name": "ng/mL", "uom_symbol": "ng/mL", "uom_category": "Concentration", "description": "Nanograms per millilitre"},
	{"uom_name": "pg/mL", "uom_symbol": "pg/mL", "uom_category": "Concentration", "description": "Picograms per millilitre"},
	{"uom_name": "mmol/L", "uom_symbol": "mmol/L", "uom_category": "Concentration", "description": "Millimoles per litre"},
	{"uom_name": "µmol/L", "uom_symbol": "µmol/L", "uom_category": "Concentration", "description": "Micromoles per litre"},
	{"uom_name": "nmol/L", "uom_symbol": "nmol/L", "uom_category": "Concentration", "description": "Nanomoles per litre"},
	{"uom_name": "mEq/L", "uom_symbol": "mEq/L", "uom_category": "Concentration", "description": "Milliequivalents per litre"},
	{"uom_name": "g/L", "uom_symbol": "g/L", "uom_category": "Concentration", "description": "Grams per litre"},
	{"uom_name": "mg/L", "uom_symbol": "mg/L", "uom_category": "Concentration", "description": "Milligrams per litre"},
	{"uom_name": "%", "uom_symbol": "%", "uom_category": "General", "description": "Percentage"},
	# Count
	{"uom_name": "cells/µL", "uom_symbol": "cells/µL", "uom_category": "Count", "description": "Cells per microlitre"},
	{"uom_name": "×10³/µL", "uom_symbol": "×10³/µL", "uom_category": "Count", "description": "Thousands per microlitre (WBC, Platelets)"},
	{"uom_name": "×10⁶/µL", "uom_symbol": "×10⁶/µL", "uom_category": "Count", "description": "Millions per microlitre (RBC)"},
	{"uom_name": "×10⁹/L", "uom_symbol": "×10⁹/L", "uom_category": "Count", "description": "Billions per litre"},
	# Activity
	{"uom_name": "IU/L", "uom_symbol": "IU/L", "uom_category": "Activity", "description": "International units per litre (enzymes)"},
	{"uom_name": "U/L", "uom_symbol": "U/L", "uom_category": "Activity", "description": "Units per litre"},
	{"uom_name": "mIU/mL", "uom_symbol": "mIU/mL", "uom_category": "Activity", "description": "Milli international units per millilitre"},
	{"uom_name": "IU/mL", "uom_symbol": "IU/mL", "uom_category": "Activity", "description": "International units per millilitre"},
	# Volume / Mass
	{"uom_name": "fL", "uom_symbol": "fL", "uom_category": "Volume", "description": "Femtolitres (MCV)"},
	{"uom_name": "pg", "uom_symbol": "pg", "uom_category": "Mass", "description": "Picograms (MCH)"},
	{"uom_name": "g/dL (Hb)", "uom_symbol": "g/dL", "uom_category": "Concentration", "description": "Haemoglobin"},
	# Ratio
	{"uom_name": "Ratio", "uom_symbol": "ratio", "uom_category": "Ratio", "description": "Dimensionless ratio"},
	{"uom_name": "INR", "uom_symbol": "INR", "uom_category": "Ratio", "description": "International Normalised Ratio (PT-INR)"},
	{"uom_name": "Titre", "uom_symbol": "titre", "uom_category": "Ratio", "description": "Antibody/agglutination titre"},
	# Time
	{"uom_name": "seconds", "uom_symbol": "sec", "uom_category": "Time", "description": "Clotting/prothrombin time"},
	{"uom_name": "mm/hr", "uom_symbol": "mm/hr", "uom_category": "General", "description": "Millimetres per hour (ESR)"},
	# General / Qualitative
	{"uom_name": "Qualitative", "uom_symbol": "Qual", "uom_category": "General", "description": "Positive/Negative result"},
	{"uom_name": "mOsm/kg", "uom_symbol": "mOsm/kg", "uom_category": "General", "description": "Milliosmoles per kilogram (osmolality)"},
	{"uom_name": "kPa", "uom_symbol": "kPa", "uom_category": "General", "description": "Kilopascals (blood gas pressures)"},
	{"uom_name": "mmHg", "uom_symbol": "mmHg", "uom_category": "General", "description": "Millimetres of mercury"},
	{"uom_name": "µIU/mL", "uom_symbol": "µIU/mL", "uom_category": "Activity", "description": "Micro international units per millilitre (Insulin, TSH)"},
	{"uom_name": "pmol/L", "uom_symbol": "pmol/L", "uom_category": "Concentration", "description": "Picomoles per litre (thyroid hormones)"},
]


def seed_lab_test_uom():
	"""Insert standard Lab Test UOM records if they don't already exist."""
	try:
		inserted = 0
		for uom in LAB_TEST_UOMS:
			if not frappe.db.exists("Lab Test UOM", uom["uom_name"]):
				doc = frappe.get_doc({"doctype": "Lab Test UOM", **uom})
				doc.insert(ignore_permissions=True)
				inserted += 1
		if inserted:
			frappe.logger().info(f"ArogyaPath: Seeded {inserted} Lab Test UOM records")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: seed_lab_test_uom failed")
