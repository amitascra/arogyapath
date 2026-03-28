# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabBranch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		branch_code: DF.Data
		branch_name: DF.Data
		city: DF.Data | None
		drug_license_number: DF.Data | None
		email: DF.Data | None
		gstin: DF.Data | None
		is_active: DF.Check
		is_head_office: DF.Check
		nabl_number: DF.Data | None
		phone: DF.Data | None
		pincode: DF.Data | None
		state: DF.Literal[None]
		state_code: DF.Data | None
	# end: auto-generated types

	def validate(self):
		"""Validate Lab Branch"""
		self.validate_gstin()
		self.validate_branch_code()

	def validate_gstin(self):
		"""Validate GSTIN format"""
		if self.gstin:
			from arogyapath.arogyapath.utils.gst import validate_gstin
			validate_gstin(self.gstin)

	def validate_branch_code(self):
		"""Validate branch code format"""
		if self.branch_code:
			self.branch_code = self.branch_code.upper()
			if len(self.branch_code) < 2 or len(self.branch_code) > 4:
				frappe.throw("Branch Code must be 2-4 characters")
