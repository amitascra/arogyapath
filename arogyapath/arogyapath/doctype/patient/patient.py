# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff
from datetime import datetime


class Patient(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		abha_id: DF.Data | None
		address: DF.SmallText | None
		age: DF.Int
		blood_group: DF.Literal[None]
		city: DF.Data | None
		date_of_birth: DF.Date
		email: DF.Data | None
		full_name: DF.Data
		gender: DF.Literal["Male", "Female", "Other"]
		id_number: DF.Data | None
		id_type: DF.Literal[None]
		is_active: DF.Check
		mobile: DF.Data
		naming_series: DF.Literal["PT-.YYYY.-.#####"]
		patient_id: DF.Data | None
		patient_notes: DF.Text | None
		pincode: DF.Data | None
		state: DF.Literal[None]
	# end: auto-generated types

	def before_save(self):
		"""Calculate age before saving"""
		self.calculate_age()
		self.patient_id = self.name

	def calculate_age(self):
		"""Calculate age from date of birth"""
		if self.date_of_birth:
			dob = getdate(self.date_of_birth)
			today = getdate()
			age_days = date_diff(today, dob)
			self.age = int(age_days / 365.25)
