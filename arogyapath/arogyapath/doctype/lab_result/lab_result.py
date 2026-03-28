# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, date_diff, getdate, today


AGE_TYPE_DAYS = {"Days": 1, "Months": 30.44, "Years": 365.25}


class LabResult(Document):
	def before_insert(self):
		if not self.entered_by:
			self.entered_by = frappe.session.user
		if not self.entered_at:
			self.entered_at = now_datetime()
		self._fetch_linked_fields()

	def validate(self):
		self._guard_amendment()
		self._run_calculated_parameters()
		for item in self.items:
			item.flag = self._compute_flag(item)
		self.has_critical_value = any(
			i.flag in ("Critical Low", "Critical High") for i in self.items
		)

	def _fetch_linked_fields(self):
		"""Populate branch/department/sample_collection from Lab Order if not set."""
		if not self.lab_order:
			return
		order_vals = frappe.db.get_value(
			"Lab Order",
			self.lab_order,
			["branch", "sample_collection", "patient", "patient_name"],
			as_dict=True,
		)
		if not order_vals:
			return
		if not self.branch:
			self.branch = order_vals.branch
		if not self.sample_collection:
			self.sample_collection = order_vals.sample_collection
		if not self.patient:
			self.patient = order_vals.patient
		if not self.patient_name:
			self.patient_name = order_vals.patient_name
		if self.test and not self.department:
			self.department = frappe.db.get_value("Lab Test Master", self.test, "department")

	def _guard_amendment(self):
		"""Prevent editing a Released result unless is_amended is checked and amendment_reason given."""
		if not self.get_doc_before_save():
			return
		prev_status = self.get_doc_before_save().validation_status
		if prev_status == "Released" and self.validation_status == "Released":
			if not self.is_amended:
				frappe.throw(
					"This result is already Released. To modify it, check <b>Is Amended</b> "
					"and provide an amendment reason."
				)
			if not self.amendment_reason:
				frappe.throw("Amendment reason is required when amending a released result.")

	def _run_calculated_parameters(self):
		"""Compute values for parameters marked is_calculated using their formula."""
		if not self.test:
			return
		test_doc = frappe.get_cached_doc("Lab Test Master", self.test)

		# Build a lookup of parameter_code → numeric result for formula eval
		values = {}
		for item in self.items:
			if item.result_numeric is not None:
				values[item.parameter_code] = item.result_numeric

		for param in test_doc.parameters:
			if not param.is_calculated or not param.calculation_formula:
				continue
			try:
				result = eval(param.calculation_formula, {"__builtins__": {}}, values)  # noqa: S307
				for item in self.items:
					if item.parameter_name == param.parameter_name:
						item.result_numeric = round(float(result), param.decimal_places or 2)
						item.result_value = str(item.result_numeric)
			except Exception:
				pass

	def _compute_flag(self, item):
		"""Compute Normal/Low/High/Critical Low/Critical High flag."""
		if item.result_numeric is None:
			return item.flag or "Normal"
		v = float(item.result_numeric)
		if item.critical_min and v < float(item.critical_min):
			return "Critical Low"
		if item.critical_max and v > float(item.critical_max):
			return "Critical High"
		if item.normal_min and v < float(item.normal_min):
			return "Low"
		if item.normal_max and v > float(item.normal_max):
			return "High"
		return "Normal"

	def on_update(self):
		"""Handle validation status transitions with permission guards."""
		prev = self.get_doc_before_save()
		prev_status = prev.validation_status if prev else None

		# Tech Approval
		if self.validation_status == "Tech Approved" and prev_status == "Draft":
			self.db_set("approved_by_tech", frappe.session.user, update_modified=False)
			self.db_set("approved_at_tech", now_datetime(), update_modified=False)

		# Pathologist Approval → auto-release
		if self.validation_status == "Pathologist Approved" and prev_status in ("Tech Approved", "Draft"):
			user_roles = frappe.get_roles(frappe.session.user)
			if "Lab Pathologist" not in user_roles and "Lab Manager" not in user_roles and "Lab Admin" not in user_roles:
				frappe.throw("Only Lab Pathologist, Lab Manager, or Lab Admin can set Pathologist Approved status.")
			self.db_set("approved_by_path", frappe.session.user, update_modified=False)
			self.db_set("approved_at_path", now_datetime(), update_modified=False)
			self.db_set("validation_status", "Released", update_modified=False)
			self._trigger_report_generation()

		# Critical value alert on any save where critical and not yet notified
		if self.has_critical_value and not self.critical_notified:
			self._send_critical_alert()

	def _trigger_report_generation(self):
		"""Auto-create Lab Report after pathologist approval (once per order)."""
		if frappe.db.exists("Lab Report", {"lab_order": self.lab_order}):
			return
		try:
			report = frappe.new_doc("Lab Report")
			report.lab_order = self.lab_order
			report.patient = self.patient
			report.branch = self.branch
			report.report_date = today()
			report.signed_by = self.approved_by_path
			report.delivery_status = "Pending"
			report.insert(ignore_permissions=True)
			frappe.db.commit()
		except Exception:
			frappe.log_error(frappe.get_traceback(), "ArogyaPath: Lab Report auto-creation failed")

	def _send_critical_alert(self):
		"""Send critical value alert via WhatsApp/SMS using Notification Template."""
		try:
			from arogyapath.arogyapath.doctype.notification_template.notification_template import NotificationTemplate

			template = NotificationTemplate.get_template("Critical Value", "WhatsApp")
			if not template:
				return

			patient = frappe.get_cached_doc("Patient", self.patient) if self.patient else None
			if not patient or not patient.mobile:
				return

			critical_params = [
				f"{i.parameter_name}: {i.result_value} {i.unit or ''} [{i.flag}]"
				for i in self.items
				if i.flag in ("Critical Low", "Critical High")
			]

			context = {
				"patient_name": patient.full_name,
				"patient_mobile": patient.mobile,
				"lab_order": self.lab_order,
				"test_name": frappe.db.get_value("Lab Test Master", self.test, "test_name"),
				"critical_values": "\n".join(critical_params),
				"branch_name": self.branch,
			}
			message = template.render(context)
			frappe.log_error(
				f"Critical alert for {self.patient}: {message}",
				"ArogyaPath: Critical Value Alert (send not wired yet)",
			)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "ArogyaPath: _send_critical_alert failed")

	@frappe.whitelist()
	def load_reference_ranges(self):
		"""
		Populate reference ranges on result items from Lab Test Master
		matched by patient age (in days) and gender.
		"""
		if not self.test or not self.patient:
			return

		patient = frappe.get_cached_doc("Patient", self.patient)
		gender = patient.gender or "Both"

		# Compute patient age in days
		age_days = 0
		if patient.date_of_birth:
			age_days = date_diff(today(), patient.date_of_birth)
		elif patient.age:
			age_days = int(patient.age) * 365

		test_doc = frappe.get_cached_doc("Lab Test Master", self.test)

		for item in self.items:
			rr = _find_reference_range(test_doc, item.parameter_name, gender, age_days)
			if rr:
				item.normal_min = rr.normal_min
				item.normal_max = rr.normal_max
				item.critical_min = rr.critical_min
				item.critical_max = rr.critical_max
				if rr.reference_display_text:
					item.reference_range_text = rr.reference_display_text
				elif rr.normal_min is not None and rr.normal_max is not None:
					item.reference_range_text = f"{rr.normal_min} – {rr.normal_max}"
				elif rr.normal_text:
					item.reference_range_text = rr.normal_text
				if rr.unit:
					item.unit = rr.unit


def _find_reference_range(test_doc, parameter_name: str, gender: str, age_days: int):
	"""
	Find the best matching Reference Range row for a given parameter/gender/age.
	Match priority: exact gender + age range > gender match > All + age range > Any
	"""
	best = None
	best_score = -1

	for rr in test_doc.get("reference_ranges", []):
		if rr.parameter != parameter_name:
			continue

		# Convert stored age_from/age_to using type to days for comparison
		rr_from_days = _to_days(rr.age_from or 0, rr.age_from_type or "Years")
		rr_to_days = _to_days(rr.age_to or 100, rr.age_to_type or "Years")

		age_ok = rr_from_days <= age_days <= rr_to_days
		gender_ok = rr.gender in (gender, "Both")

		if not age_ok or not gender_ok:
			continue

		score = 0
		if rr.gender == gender:
			score += 2
		if rr_from_days > 0 or rr_to_days < 36525:
			score += 1

		if score > best_score:
			best_score = score
			best = rr

	return best


def _to_days(value: float, unit: str) -> int:
	"""Convert age value + unit to integer days."""
	multiplier = AGE_TYPE_DAYS.get(unit, 365.25)
	return int(float(value or 0) * multiplier)
