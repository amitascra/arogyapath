# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TaxCategory(Document):
	def validate(self):
		"""Validate tax category"""
		self.validate_duplicate()
	
	def validate_duplicate(self):
		"""Check for duplicate tax categories with same configuration"""
		if self.is_new():
			existing = frappe.db.exists(
				"Tax Category",
				{
					"is_inter_state": self.is_inter_state,
					"is_reverse_charge": self.is_reverse_charge,
					"gst_state": self.gst_state or "",
					"name": ["!=", self.name],
					"disabled": 0
				}
			)
			if existing:
				frappe.msgprint(
					f"A similar tax category '{existing}' already exists with the same configuration.",
					indicator="orange",
					alert=True
				)
