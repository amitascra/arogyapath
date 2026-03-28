# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Doctor(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		bank_account: DF.Data | None
		commission_on: DF.Literal["Gross", "Net"]
		commission_rate: DF.Float
		commission_type: DF.Literal["None", "Percentage", "Fixed Per Test"]
		doctor_code: DF.Data | None
		doctor_name: DF.Data
		email: DF.Data | None
		gstin: DF.Data | None
		hospital_clinic: DF.Data | None
		ifsc: DF.Data | None
		is_active: DF.Check
		mobile: DF.Data | None
		pan: DF.Data | None
		settlement_frequency: DF.Literal["Monthly", "Quarterly"]
		specialization: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate Doctor"""
		if self.gstin:
			from arogyapath.arogyapath.utils.gst import validate_gstin
			validate_gstin(self.gstin)
