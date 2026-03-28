# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class QCResult(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.qc_result_item.qc_result_item import QCResultItem

		analyzer: DF.Link
		branch: DF.Link
		department: DF.Link
		entered_by: DF.Link | None
		items: DF.Table[QCResultItem]
		material_level: DF.Data | None
		naming_series: DF.Literal["QCR-.YYYY.-.#####"]
		overall_status: DF.Literal["Pass", "Warning", "Reject"]
		qc_material: DF.Link
		remarks: DF.SmallText | None
		run_date: DF.Date
		run_time: DF.Time | None
	# end: auto-generated types

	def before_insert(self):
		if not self.entered_by:
			self.entered_by = frappe.session.user
		if not self.run_time:
			self.run_time = now_datetime().strftime("%H:%M:%S")

	def validate(self):
		self._compute_z_scores()
		self._apply_westgard_rules()
		self._set_overall_status()

	def _compute_z_scores(self):
		"""Compute Z-score for each parameter"""
		material = frappe.get_doc("QC Material", self.qc_material)
		for item in self.items:
			if material.target_sd and material.target_sd != 0:
				item.target_mean = material.target_mean
				item.target_sd = material.target_sd
				item.z_score = flt((item.observed_value - material.target_mean) / material.target_sd, 3)

	def _apply_westgard_rules(self):
		"""Apply Westgard rules to flag each item"""
		for item in self.items:
			z = flt(item.z_score)
			if abs(z) >= 3:
				item.westgard_flag = "1-3s Reject"
			elif abs(z) >= 2:
				item.westgard_flag = "1-2s Warning"
			else:
				item.westgard_flag = "Pass"

	def _set_overall_status(self):
		"""Set overall status based on worst item flag"""
		flags = [i.westgard_flag for i in self.items]
		if any("Reject" in f for f in flags):
			self.overall_status = "Reject"
		elif any("Warning" in f for f in flags):
			self.overall_status = "Warning"
		else:
			self.overall_status = "Pass"
