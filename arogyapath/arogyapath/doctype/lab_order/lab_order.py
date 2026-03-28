# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date


class LabOrder(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.lab_order_item.lab_order_item import LabOrderItem

		branch: DF.Link | None
		clinical_notes: DF.SmallText | None
		invoice: DF.Link | None
		naming_series: DF.Literal["LO-.BRANCH.-.YYYY.-.#####"]
		order_date: DF.Date
		order_time: DF.Time | None
		patient: DF.Link | None
		patient_name: DF.Data | None
		patient_visit: DF.Link
		priority: DF.Literal["Routine", "Urgent", "STAT"]
		referred_by: DF.Link | None
		sample_collection: DF.Link | None
		status: DF.Literal["Draft", "Confirmed", "Processing", "Resulted", "Cancelled"]
		tests: DF.Table[LabOrderItem]
	# end: auto-generated types

	def before_insert(self):
		if not self.order_time:
			self.order_time = now_datetime().strftime("%H:%M:%S")

	def before_save(self):
		self.set_tat_deadlines()

	def set_tat_deadlines(self):
		"""Compute TAT deadline for each test item"""
		order_dt_str = f"{self.order_date} {self.order_time or '00:00:00'}"
		for item in self.tests:
			if item.test and not item.tat_deadline:
				tat_hours = frappe.db.get_value("Lab Test Master", item.test, "tat_hours") or 24
				item.tat_deadline = add_to_date(order_dt_str, hours=tat_hours)

	def on_submit(self):
		self.status = "Confirmed"
		frappe.db.set_value("Patient Visit", self.patient_visit, "status", "Sample Collected")

	def on_cancel(self):
		self.status = "Cancelled"
		for item in self.tests:
			item.status = "Cancelled"
