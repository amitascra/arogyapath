# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabDepartment(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		department_code: DF.Data
		department_name: DF.Data
		head_pathologist: DF.Link | None
		report_template: DF.Link | None
		sort_order: DF.Int
		turnaround_hours: DF.Int
	# end: auto-generated types

	def validate(self):
		"""Validate Lab Department"""
		if self.department_code:
			self.department_code = self.department_code.upper()
