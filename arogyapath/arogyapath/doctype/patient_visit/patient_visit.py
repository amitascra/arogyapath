# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class PatientVisit(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link
		clinical_notes: DF.SmallText | None
		naming_series: DF.Literal["VIS-.BRANCH.-.YYYY.-.#####"]
		patient: DF.Link
		patient_name: DF.Data | None
		referred_by: DF.Link | None
		referral_slip_no: DF.Data | None
		status: DF.Literal["Open", "Sample Collected", "Resulted", "Completed"]
		visit_date: DF.Date
		visit_time: DF.Time | None
		visit_type: DF.Literal["Walk-in", "Appointment", "Home Collection"]
	# end: auto-generated types

	def before_insert(self):
		"""Set visit time if not provided"""
		if not self.visit_time:
			self.visit_time = now_datetime().strftime("%H:%M:%S")
