# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class GLEntry(Document):
	def validate(self):
		"""Validate GL Entry"""
		self.validate_debit_credit()
		self.validate_account()
	
	def validate_debit_credit(self):
		"""Ensure either debit or credit is set, not both"""
		if flt(self.debit) > 0 and flt(self.credit) > 0:
			frappe.throw(_("Both Debit and Credit cannot be greater than zero"))
		
		if flt(self.debit) == 0 and flt(self.credit) == 0:
			frappe.throw(_("Either Debit or Credit must be greater than zero"))
	
	def validate_account(self):
		"""Validate account exists and is not a group"""
		account = frappe.get_cached_doc("Account", self.account)
		if account.is_group:
			frappe.throw(_("Cannot make GL Entry against group account {0}").format(self.account))
	
	def on_submit(self):
		"""Update account balance on submit"""
		self.update_account_balance()
	
	def on_cancel(self):
		"""Reverse account balance on cancel"""
		self.reverse_account_balance()
	
	def update_account_balance(self):
		"""Update account balance"""
		account = frappe.get_doc("Account", self.account)
		if flt(self.debit) > 0:
			account.update_balance(self.debit, "Debit")
		else:
			account.update_balance(self.credit, "Credit")
	
	def reverse_account_balance(self):
		"""Reverse account balance"""
		account = frappe.get_doc("Account", self.account)
		if flt(self.debit) > 0:
			account.update_balance(self.debit, "Credit")
		else:
			account.update_balance(self.credit, "Debit")


def make_gl_entries(voucher_type, voucher_no, gl_map, posting_date=None, company=None, branch=None):
	"""
	Create GL Entries for a voucher
	
	Args:
		voucher_type: DocType name (e.g., "Lab Invoice")
		voucher_no: Document name
		gl_map: List of dicts with account, debit, credit, party_type, party, against, remarks
		posting_date: Posting date (default: today)
		company: Company
		branch: Lab Branch
	"""
	from frappe.utils import today
	
	if not posting_date:
		posting_date = today()
	
	# Validate total debits = total credits
	total_debit = sum(flt(d.get("debit", 0)) for d in gl_map)
	total_credit = sum(flt(d.get("credit", 0)) for d in gl_map)
	
	if abs(total_debit - total_credit) > 0.01:
		frappe.throw(_("Total Debit ({0}) must equal Total Credit ({1})").format(total_debit, total_credit))
	
	# Create GL Entries
	for entry in gl_map:
		gl_entry = frappe.new_doc("GL Entry")
		gl_entry.posting_date = posting_date
		gl_entry.account = entry.get("account")
		gl_entry.party_type = entry.get("party_type")
		gl_entry.party = entry.get("party")
		gl_entry.debit = flt(entry.get("debit", 0))
		gl_entry.credit = flt(entry.get("credit", 0))
		gl_entry.against = entry.get("against")
		gl_entry.voucher_type = voucher_type
		gl_entry.voucher_no = voucher_no
		gl_entry.company = company
		gl_entry.branch = branch
		gl_entry.remarks = entry.get("remarks")
		gl_entry.insert(ignore_permissions=True)
		gl_entry.submit()


def cancel_gl_entries(voucher_type, voucher_no):
	"""Cancel all GL Entries for a voucher"""
	gl_entries = frappe.get_all(
		"GL Entry",
		filters={"voucher_type": voucher_type, "voucher_no": voucher_no, "is_cancelled": 0},
		pluck="name"
	)
	
	for name in gl_entries:
		gl_entry = frappe.get_doc("GL Entry", name)
		gl_entry.cancel()
		gl_entry.is_cancelled = 1
		gl_entry.save(ignore_permissions=True)
