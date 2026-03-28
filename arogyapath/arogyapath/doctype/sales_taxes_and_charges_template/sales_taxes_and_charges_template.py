# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SalesTaxesandChargesTemplate(Document):
	def validate(self):
		"""Validate tax template"""
		self.validate_taxes()
		self.validate_default()
	
	def validate_taxes(self):
		"""Ensure at least one tax row exists"""
		if not self.taxes:
			frappe.throw(_("Please add at least one tax row"))
	
	def validate_default(self):
		"""Ensure only one default template per pathology lab and tax category"""
		if self.is_default:
			# Check for other default templates
			filters = {
				"pathology_lab": self.pathology_lab,
				"is_default": 1,
				"name": ["!=", self.name],
				"disabled": 0
			}
			
			if self.tax_category:
				filters["tax_category"] = self.tax_category
			
			existing = frappe.db.exists("Sales Taxes and Charges Template", filters)
			
			if existing:
				frappe.throw(
					_("Another default template '{0}' already exists for this Pathology Lab and Tax Category").format(existing)
				)
