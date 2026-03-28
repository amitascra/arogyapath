"""
ArogyaPath Phase 9 — Indian Pathology Test Catalog Seed Data
Covers ~120 Lab Test Masters, 25 Health Check Panels, 9 Departments, 10 Sample Types.
All data modelled on Dr Lal PathLabs, SRL/Agilus, Metropolis, Thyrocare Aarogyam.
Called from install.py::after_migrate() — fully idempotent.
"""

import frappe


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _upsert_dept(data):
	if frappe.db.exists("Lab Department", data["department_name"]):
		return
	frappe.get_doc({"doctype": "Lab Department", **data}).insert(ignore_permissions=True)


def _upsert_sample(data):
	if frappe.db.exists("Sample Type", data["sample_type_name"]):
		return
	frappe.get_doc({"doctype": "Sample Type", **data}).insert(ignore_permissions=True)


def _upsert_panel(data):
	if frappe.db.exists("Lab Test Panel", data["panel_code"]):
		return
	items = []
	for code in data.get("test_codes", []):
		if frappe.db.exists("Lab Test Master", code):
			items.append({"test": code})
	if not items:
		frappe.logger().warning(f"ArogyaPath: Panel {data['panel_code']} has no valid tests, skipping")
		return
	frappe.get_doc({
		"doctype": "Lab Test Panel",
		"panel_name": data["panel_name"],
		"panel_code": data["panel_code"],
		"panel_price": data["cost"],
		"is_active": 1,
		"description": data.get("description", ""),
		"tests": items,
	}).insert(ignore_permissions=True)


def _rr(param, gender="Both", age_from=0, age_from_type="Years",
		age_to=100, age_to_type="Years",
		nmin=None, nmax=None, cmin=None, cmax=None,
		normal_text=None, display=None):
	return {
		"parameter": param, "gender": gender,
		"age_from": age_from, "age_from_type": age_from_type,
		"age_to": age_to, "age_to_type": age_to_type,
		"nmin": nmin, "nmax": nmax, "cmin": cmin, "cmax": cmax,
		"normal_text": normal_text or "", "display": display or "",
	}


def _p(name, code, unit=None, rtype="Numeric", order=0, heading="",
	   bold=0, decimals=2, calc=0, formula="", options=""):
	return {
		"parameter_name": name, "parameter_code": code, "unit": unit,
		"result_type": rtype, "sort_order": order, "sub_heading": heading,
		"print_bold": bold, "decimal_places": decimals,
		"is_calculated": calc, "calculation_formula": formula,
		"options_list": options,
	}


def _abx_rows(antibiotics, extra_head_rows=None):
	rows = list(extra_head_rows or [])
	for i, abx in enumerate(antibiotics, start=len(rows) + 1):
		code = abx.replace("-", "").replace(" ", "")[:8].upper()
		rows.append(_p(abx, code, rtype="Multiple Choice", order=i,
					   heading="Antibiogram",
					   options="Sensitive\nIntermediate\nResistant\nNot Tested"))
	return rows


def _abx_urine():
	head = [
		_p("Organism", "ORG", rtype="Text", order=1, heading="Culture Result", bold=1),
		_p("Colony Count", "COLONY", rtype="Text", order=2, heading="Culture Result"),
		_p("Gram Stain", "GRAM", rtype="Text", order=3, heading="Culture Result"),
	]
	abx = ["Ampicillin", "Amoxicillin-Clavulanate", "Ciprofloxacin", "Levofloxacin",
		   "Nitrofurantoin", "Cefuroxime", "Ceftriaxone", "Cefepime",
		   "Imipenem", "Meropenem", "Co-trimoxazole", "Gentamicin", "Amikacin",
		   "Piperacillin-Tazobactam", "Norfloxacin"]
	return head + _abx_rows(abx)


def _abx_blood():
	head = [
		_p("Organism", "ORG", rtype="Text", order=1, heading="Culture Result", bold=1),
		_p("Gram Stain", "GRAM", rtype="Text", order=2, heading="Culture Result"),
		_p("Incubation Period", "INCUB", rtype="Text", order=3, heading="Culture Result"),
	]
	abx = ["Ampicillin", "Piperacillin-Tazobactam", "Ceftriaxone", "Cefepime",
		   "Imipenem", "Meropenem", "Vancomycin", "Linezolid",
		   "Amikacin", "Gentamicin", "Ciprofloxacin", "Co-trimoxazole",
		   "Clindamycin", "Metronidazole"]
	return head + _abx_rows(abx)


def _abx_sputum():
	head = [
		_p("Organism", "ORG", rtype="Text", order=1, heading="Culture Result", bold=1),
		_p("Gram Stain", "GRAM", rtype="Text", order=2, heading="Culture Result"),
	]
	abx = ["Amoxicillin-Clavulanate", "Ceftriaxone", "Azithromycin",
		   "Levofloxacin", "Moxifloxacin", "Imipenem", "Amikacin",
		   "Piperacillin-Tazobactam", "Co-trimoxazole"]
	return head + _abx_rows(abx)


# ---------------------------------------------------------------------------
# 9A — Lab Departments
# ---------------------------------------------------------------------------

DEPARTMENTS = [
	{"department_name": "Haematology",          "department_code": "HAEM",    "turnaround_hours": 4,  "sort_order": 1},
	{"department_name": "Biochemistry",          "department_code": "BIOCHEM", "turnaround_hours": 6,  "sort_order": 2},
	{"department_name": "Clinical Pathology",    "department_code": "CLINPATH","turnaround_hours": 12, "sort_order": 3},
	{"department_name": "Serology & Immunology", "department_code": "SERO",    "turnaround_hours": 6,  "sort_order": 4},
	{"department_name": "Microbiology",          "department_code": "MICRO",   "turnaround_hours": 48, "sort_order": 5},
	{"department_name": "Endocrinology",         "department_code": "ENDO",    "turnaround_hours": 24, "sort_order": 6},
	{"department_name": "Tumor Markers",         "department_code": "TUMOR",   "turnaround_hours": 24, "sort_order": 7},
	{"department_name": "Virology & Molecular",  "department_code": "VIRAL",   "turnaround_hours": 48, "sort_order": 8},
	{"department_name": "Special Tests",         "department_code": "SPECIAL", "turnaround_hours": 24, "sort_order": 9},
]


def seed_lab_departments():
	try:
		for d in DEPARTMENTS:
			_upsert_dept(d)
		frappe.logger().info("ArogyaPath: Seeded lab departments")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: seed_lab_departments failed")


# ---------------------------------------------------------------------------
# 9B — Sample Types
# ---------------------------------------------------------------------------

SAMPLE_TYPES = [
	{
		"sample_type_name": "Whole Blood (EDTA)",
		"specimen_code": "EDTA",
		"container_type": "EDTA Tube", "tube_color": "Purple",
		"storage_temp": "2-8°C", "stability_hours": 24, "minimum_volume_ml": 2.0,
		"collection_instructions": "No special preparation required.",
		"handling_notes": "Mix gently by inversion 8-10 times. Do not shake.",
	},
	{
		"sample_type_name": "Serum (Plain)",
		"specimen_code": "SERUM",
		"container_type": "Plain", "tube_color": "Red",
		"storage_temp": "2-8°C", "stability_hours": 48, "minimum_volume_ml": 3.0,
		"collection_instructions": "Fasting 8-12 hours required for lipid/glucose tests.",
		"handling_notes": "Allow to clot 30 min, then centrifuge at 3000 rpm for 10 min.",
	},
	{
		"sample_type_name": "Plasma (Fluoride)",
		"specimen_code": "FLUORIDE",
		"container_type": "Fluoride", "tube_color": "Grey",
		"storage_temp": "2-8°C", "stability_hours": 24, "minimum_volume_ml": 2.0,
		"collection_instructions": "Fasting 8-12 hours required for glucose tests.",
		"handling_notes": "Mix gently. Process within 1 hour of collection.",
	},
	{
		"sample_type_name": "Plasma (Citrate)",
		"specimen_code": "CITRATE",
		"container_type": "Plain", "tube_color": "Blue",
		"storage_temp": "2-8°C", "stability_hours": 4, "minimum_volume_ml": 2.7,
		"collection_instructions": "No special preparation.",
		"handling_notes": "Fill tube exactly to mark (9:1 ratio). Process within 4 hours.",
	},
	{
		"sample_type_name": "Urine (Random)",
		"specimen_code": "URINE",
		"container_type": "Urine Cup", "tube_color": "White",
		"storage_temp": "2-8°C", "stability_hours": 2, "minimum_volume_ml": 10.0,
		"collection_instructions": "Collect midstream urine in a clean dry container.",
		"handling_notes": "Process within 2 hours. Refrigerate if delayed.",
	},
	{
		"sample_type_name": "Urine (First Morning)",
		"specimen_code": "URINE-FM",
		"container_type": "Urine Cup", "tube_color": "White",
		"storage_temp": "2-8°C", "stability_hours": 2, "minimum_volume_ml": 10.0,
		"collection_instructions": "Collect first morning midstream urine sample.",
		"handling_notes": "Process within 2 hours of collection.",
	},
	{
		"sample_type_name": "Stool",
		"specimen_code": "STOOL",
		"container_type": "Stool Container", "tube_color": "White",
		"storage_temp": "2-8°C", "stability_hours": 24, "minimum_volume_ml": 5.0,
		"collection_instructions": "Collect a small portion of fresh stool. Avoid urine contamination.",
		"handling_notes": "Examine within 2 hours for best results.",
	},
	{
		"sample_type_name": "Sputum",
		"specimen_code": "SPUTUM",
		"container_type": "Plain", "tube_color": "White",
		"storage_temp": "2-8°C", "stability_hours": 4, "minimum_volume_ml": 3.0,
		"collection_instructions": "Collect early morning sputum. Rinse mouth with water before collection. Cough deeply.",
		"handling_notes": "Process within 4 hours. Do not refrigerate for AFB.",
	},
	{
		"sample_type_name": "Swab",
		"specimen_code": "SWAB",
		"container_type": "Swab", "tube_color": "White",
		"storage_temp": "Room Temp", "stability_hours": 6, "minimum_volume_ml": 0.0,
		"collection_instructions": "Swab the affected area firmly. Insert into transport medium immediately.",
		"handling_notes": "Transport in Amies/Stuart medium. Process within 6 hours.",
	},
	{
		"sample_type_name": "Semen",
		"specimen_code": "SEMEN",
		"container_type": "Plain", "tube_color": "White",
		"storage_temp": "Room Temp", "stability_hours": 1, "minimum_volume_ml": 2.0,
		"collection_instructions": "Abstain 2-5 days. Collect entire sample by masturbation into provided container.",
		"handling_notes": "Process within 1 hour at body temperature. Do not refrigerate.",
	},
]


def seed_sample_types():
	try:
		for s in SAMPLE_TYPES:
			_upsert_sample(s)
		frappe.logger().info("ArogyaPath: Seeded sample types")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: seed_sample_types failed")


# ---------------------------------------------------------------------------
# 9C — Lab Tests (imported from seed_tests.py)
# ---------------------------------------------------------------------------

def seed_lab_tests():
	try:
		from arogyapath.arogyapath.seed_tests import LAB_TESTS
		inserted = 0
		for test in LAB_TESTS:
			if frappe.db.exists("Lab Test Master", test["test_code"]):
				continue
			dept_name = test.get("department")
			sample_name = test.get("sample_type")
			if not frappe.db.exists("Lab Department", dept_name):
				frappe.logger().warning(f"ArogyaPath: Department '{dept_name}' missing, skip {test['test_code']}")
				continue
			if not frappe.db.exists("Sample Type", sample_name):
				frappe.logger().warning(f"ArogyaPath: Sample Type '{sample_name}' missing, skip {test['test_code']}")
				continue

			doc = frappe.get_doc({
				"doctype": "Lab Test Master",
				"test_name": test["test_name"],
				"test_code": test["test_code"],
				"department": dept_name,
				"sample_type": sample_name,
				"method": test.get("method", ""),
				"tat_hours": test.get("tat_hours", 24),
				"cost": test.get("cost", 0),
				"is_active": 1,
				"is_gst_exempt": 1,
				"is_outsourced": test.get("is_outsourced", 0),
				"hsn_sac_code": "999316",
				"report_format": test.get("report_format", "Standard"),
				"methodology_note": test.get("methodology_note", ""),
			})

			for p in test.get("parameters", []):
				row = {
					"parameter_name": p["parameter_name"],
					"parameter_code": p["parameter_code"],
					"result_type": p.get("result_type", "Numeric"),
					"sort_order": p.get("sort_order", 0),
					"sub_heading": p.get("sub_heading", ""),
					"print_bold": p.get("print_bold", 0),
					"decimal_places": p.get("decimal_places", 2),
					"is_calculated": p.get("is_calculated", 0),
					"calculation_formula": p.get("calculation_formula", ""),
					"options_list": p.get("options_list", ""),
				}
				if p.get("unit") and frappe.db.exists("Lab Test UOM", p["unit"]):
					row["unit"] = p["unit"]
				doc.append("parameters", row)

			for rr in test.get("reference_ranges", []):
				doc.append("reference_ranges", {
					"parameter": rr["parameter"],
					"gender": rr.get("gender", "Both"),
					"age_from": rr.get("age_from", 0),
					"age_from_type": rr.get("age_from_type", "Years"),
					"age_to": rr.get("age_to", 100),
					"age_to_type": rr.get("age_to_type", "Years"),
					"normal_min": rr.get("nmin"),
					"normal_max": rr.get("nmax"),
					"critical_min": rr.get("cmin"),
					"critical_max": rr.get("cmax"),
					"normal_text": rr.get("normal_text", ""),
					"reference_display_text": rr.get("display", ""),
				})

			doc.insert(ignore_permissions=True)
			inserted += 1

		frappe.logger().info(f"ArogyaPath: Seeded {inserted} Lab Test Master records")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: seed_lab_tests failed")


# ---------------------------------------------------------------------------
# 9D — Lab Test Panels (imported from seed_panels.py)
# ---------------------------------------------------------------------------

def seed_lab_test_panels():
	try:
		from arogyapath.arogyapath.seed_panels import LAB_TEST_PANELS
		inserted = 0
		for panel in LAB_TEST_PANELS:
			if not frappe.db.exists("Lab Test Panel", panel["panel_name"]):
				_upsert_panel(panel)
				inserted += 1
		frappe.logger().info(f"ArogyaPath: Seeded {inserted} Lab Test Panel records")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: seed_lab_test_panels failed")
