# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabTestMaster(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.test_parameter.test_parameter import TestParameter
		from arogyapath.arogyapath.doctype.reference_range.reference_range import ReferenceRange

		cost: DF.Currency
		department: DF.Link
		hsn_sac_code: DF.Data | None
		is_active: DF.Check
		is_gst_exempt: DF.Check
		is_outsourced: DF.Check
		method: DF.Data | None
		methodology_note: DF.Text | None
		outsource_cost: DF.Currency
		outsource_lab: DF.Data | None
		parameters: DF.Table[TestParameter]
		reference_ranges: DF.Table[ReferenceRange]
		report_format: DF.Literal["Standard", "Microscopy", "Culture", "Cytology"]
		sample_type: DF.Link
		tat_hours: DF.Int
		test_code: DF.Data
		test_name: DF.Data
	# end: auto-generated types

	def validate(self):
		"""Validate Lab Test Master"""
		if self.test_code:
			self.test_code = self.test_code.upper()
		if not self.hsn_sac_code:
			self.hsn_sac_code = "999316"
		if not self.tat_hours and self.department:
			dept_tat = frappe.db.get_value("Lab Department", self.department, "turnaround_hours")
			if dept_tat:
				self.tat_hours = dept_tat

	def get_reference_range(self, parameter_name, gender, age_days):
		"""Get matching reference range for a parameter given gender and age"""
		for rr in self.reference_ranges:
			if (rr.parameter == parameter_name
				and (rr.gender == "Both" or rr.gender == gender)
				and rr.age_from_days <= age_days <= rr.age_to_days):
				return rr
		return None
