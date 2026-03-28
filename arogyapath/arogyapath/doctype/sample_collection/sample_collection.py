# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class SampleCollection(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.sample_tube.sample_tube import SampleTube

		barcode_printed: DF.Check
		branch: DF.Link | None
		collected_by: DF.Link
		collection_center: DF.Link | None
		collection_date: DF.Date
		collection_time: DF.Time | None
		naming_series: DF.Literal["ACC-.BRANCH.-.YYYYMMDD.-.####"]
		patient: DF.Link | None
		patient_name: DF.Data | None
		patient_visit: DF.Link
		received_at: DF.Datetime | None
		received_by: DF.Link | None
		rejection_reason: DF.Literal[None]
		status: DF.Literal["Pending", "Collected", "Received", "Rejected"]
		tubes: DF.Table[SampleTube]
	# end: auto-generated types

	def before_insert(self):
		"""Set collection time if not provided"""
		if not self.collection_time:
			self.collection_time = now_datetime().strftime("%H:%M:%S")
		if not self.collected_by:
			self.collected_by = frappe.session.user

	def on_update(self):
		"""Update patient visit status when sample is collected"""
		if self.status == "Collected":
			frappe.db.set_value("Patient Visit", self.patient_visit, "status", "Sample Collected")
