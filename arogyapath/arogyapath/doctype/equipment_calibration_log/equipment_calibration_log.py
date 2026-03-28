# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, date_diff, getdate, today


class EquipmentCalibrationLog(Document):
	def validate(self):
		self._validate_dates()
		self._update_analyzer_calibration()

	def _validate_dates(self):
		if self.next_due_date and self.calibration_date:
			if getdate(self.next_due_date) <= getdate(self.calibration_date):
				frappe.throw("Next Due Date must be after Calibration Date")

	def _update_analyzer_calibration(self):
		if self.calibration_result == "Pass" and self.next_due_date:
			frappe.db.set_value(
				"Analyzer",
				self.analyzer,
				"last_calibration_date",
				self.calibration_date,
			)

	def on_submit(self):
		days_to_due = date_diff(self.next_due_date, today())
		if days_to_due <= 0:
			frappe.msgprint(
				f"Warning: Next calibration due date {self.next_due_date} is today or in the past.",
				indicator="orange",
			)
