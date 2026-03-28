# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class Account(Document):
	def validate(self):
		"""Validate account before saving"""
		self.validate_parent_account()
		self.validate_root_type()
	
	def validate_parent_account(self):
		"""Validate parent account hierarchy"""
		if self.parent_account:
			parent = frappe.get_cached_doc("Account", self.parent_account)
			if not parent.is_group:
				frappe.throw(_("Parent Account {0} must be a group account").format(self.parent_account))
			
			# Inherit root_type from parent
			if parent.root_type and not self.root_type:
				self.root_type = parent.root_type
	
	def validate_root_type(self):
		"""Validate root type consistency"""
		if self.parent_account:
			parent = frappe.get_cached_doc("Account", self.parent_account)
			if parent.root_type != self.root_type:
				frappe.throw(
					_("Root Type {0} must match parent account's Root Type {1}").format(
						self.root_type, parent.root_type
					)
				)
	
	def update_balance(self, amount, debit_or_credit):
		"""Update account balance"""
		if debit_or_credit == "Debit":
			if self.root_type in ["Asset", "Expense"]:
				self.balance = flt(self.balance) + flt(amount)
			else:
				self.balance = flt(self.balance) - flt(amount)
		else:  # Credit
			if self.root_type in ["Asset", "Expense"]:
				self.balance = flt(self.balance) - flt(amount)
			else:
				self.balance = flt(self.balance) + flt(amount)
		
		self.save(ignore_permissions=True)
