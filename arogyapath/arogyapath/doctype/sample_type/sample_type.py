# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SampleType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		collection_instructions: DF.Text | None
		container_type: DF.Literal[None]
		handling_notes: DF.Text | None
		minimum_volume_ml: DF.Float
		sample_type_name: DF.Data
		specimen_code: DF.Data
		stability_hours: DF.Int
		storage_temp: DF.Literal[None]
		tube_color: DF.Literal[None]
	# end: auto-generated types

	def validate(self):
		"""Validate Sample Type"""
		if self.specimen_code:
			self.specimen_code = self.specimen_code.upper()
