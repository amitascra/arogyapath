# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from arogyapath.arogyapath.utils.gst import validate_gstin


class Supplier(Document):
	def validate(self):
		"""Validate supplier details"""
		self.validate_gstin_format()
		self.validate_pan_format()
	
	def validate_gstin_format(self):
		"""Validate GSTIN format if provided"""
		if self.gstin:
			try:
				validate_gstin(self.gstin)
			except Exception as e:
				frappe.throw(_("Invalid GSTIN: {0}").format(str(e)))
	
	def validate_pan_format(self):
		"""Validate PAN format if provided"""
		if self.pan:
			# PAN format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
			import re
			pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
			if not re.match(pan_pattern, self.pan.upper()):
				frappe.throw(_("Invalid PAN format. Expected format: ABCDE1234F"))
			
			# Auto-uppercase PAN
			self.pan = self.pan.upper()
