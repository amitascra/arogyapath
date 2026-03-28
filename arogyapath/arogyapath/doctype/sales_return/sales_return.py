# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class SalesReturn(Document):
	def validate(self):
		"""Validate sales return before saving"""
		self.validate_return_against()
		self.calculate_item_amounts()
		self.calculate_taxes()
		self.calculate_totals()
		self.set_outstanding_amount()
	
	def on_submit(self):
		"""Update original invoice outstanding on submission"""
		self.update_invoice_outstanding()
		self.set_outstanding_amount()
	
	def on_cancel(self):
		"""Reverse outstanding updates on cancellation"""
		self.reverse_invoice_outstanding()
		self.set_outstanding_amount()
	
	def validate_return_against(self):
		"""Validate the original invoice"""
		if not self.return_against:
			frappe.throw(_("Return Against is mandatory"))
		
		# Check if invoice exists
		if not frappe.db.exists("Lab Invoice", self.return_against):
			frappe.throw(_("Lab Invoice {0} does not exist").format(self.return_against))
		
		# Fetch invoice details
		invoice = frappe.get_doc("Lab Invoice", self.return_against)
		
		# Set patient and branch
		self.patient = invoice.patient
		self.patient_name = invoice.patient_name
		self.branch = invoice.branch
	
	def calculate_item_amounts(self):
		"""Calculate amount for each item"""
		for item in self.items:
			# Basic amount = qty * rate
			item.amount = flt(item.qty) * flt(item.rate)
	
	def calculate_taxes(self):
		"""Calculate taxes based on original invoice tax structure"""
		if not self.return_against:
			return
		
		# Get original invoice
		invoice = frappe.get_doc("Lab Invoice", self.return_against)
		
		# Calculate proportional taxes
		if invoice.grand_total > 0:
			tax_ratio = (invoice.total_cgst + invoice.total_sgst + invoice.total_igst) / invoice.base_total
			
			# Apply same tax ratio to return
			self.total_cgst = flt(self.base_total * (invoice.total_cgst / invoice.base_total), 2) if invoice.base_total > 0 else 0
			self.total_sgst = flt(self.base_total * (invoice.total_sgst / invoice.base_total), 2) if invoice.base_total > 0 else 0
			self.total_igst = flt(self.base_total * (invoice.total_igst / invoice.base_total), 2) if invoice.base_total > 0 else 0
			
			self.total_tax = self.total_cgst + self.total_sgst + self.total_igst
		else:
			self.total_cgst = 0
			self.total_sgst = 0
			self.total_igst = 0
			self.total_tax = 0
	
	def calculate_totals(self):
		"""Calculate grand totals"""
		# Total quantity
		self.total_qty = sum(flt(d.qty) for d in self.items)
		
		# Base total (before tax)
		self.base_total = sum(flt(d.amount) for d in self.items)
		
		# Grand total (including tax)
		self.grand_total = self.base_total + self.total_tax
		
		# Convert to words
		from frappe.utils import money_in_words
		self.in_words = money_in_words(self.grand_total, "INR")
	
	def set_outstanding_amount(self):
		"""Set outstanding amount for refund tracking"""
		if self.docstatus == 0:
			# Draft - outstanding = grand total
			self.outstanding_amount = self.grand_total
			self.return_status = "Pending"
		elif self.docstatus == 1:
			# Submitted - calculate from payments
			refunded_amount = self.get_total_refunded_amount()
			self.outstanding_amount = flt(self.grand_total) - flt(refunded_amount)
			
			# Update return status
			if self.outstanding_amount <= 0:
				self.return_status = "Refunded"
			elif refunded_amount > 0:
				self.return_status = "Partially Refunded"
			else:
				self.return_status = "Pending"
		elif self.docstatus == 2:
			# Cancelled
			self.outstanding_amount = 0
			self.return_status = "Cancelled"
	
	def get_total_refunded_amount(self):
		"""Get total amount refunded via Payment Entry"""
		refunded_amount = frappe.db.sql("""
			SELECT SUM(per.allocated_amount)
			FROM `tabPayment Entry Reference` per
			INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
			WHERE per.reference_doctype = 'Sales Return'
				AND per.reference_name = %s
				AND pe.docstatus = 1
		""", self.name)
		
		return flt(refunded_amount[0][0]) if refunded_amount else 0
	
	def update_invoice_outstanding(self):
		"""Reduce outstanding amount in original invoice"""
		if not self.return_against:
			return
		
		try:
			invoice = frappe.get_doc("Lab Invoice", self.return_against)
			
			# Reduce outstanding by return amount
			invoice.outstanding_amount = flt(invoice.outstanding_amount) - flt(self.grand_total)
			
			# Update payment status
			if invoice.outstanding_amount <= 0:
				invoice.payment_status = "Paid"
			elif invoice.outstanding_amount < invoice.grand_total:
				invoice.payment_status = "Partly Paid"
			
			invoice.flags.ignore_validate_update_after_submit = True
			invoice.save(ignore_permissions=True)
			
			frappe.logger().info(
				f"Sales Return {self.name}: Reduced outstanding for Lab Invoice {self.return_against}"
			)
		
		except Exception as e:
			frappe.log_error(
				message=frappe.get_traceback(),
				title=f"Sales Return Outstanding Update Failed: {self.name}"
			)
			frappe.throw(
				_("Failed to update outstanding for Lab Invoice {0}. Error: {1}").format(
					self.return_against, str(e)
				)
			)
	
	def reverse_invoice_outstanding(self):
		"""Reverse outstanding reduction on cancellation"""
		if not self.return_against:
			return
		
		try:
			invoice = frappe.get_doc("Lab Invoice", self.return_against)
			
			# Add back the return amount
			invoice.outstanding_amount = flt(invoice.outstanding_amount) + flt(self.grand_total)
			
			# Update payment status
			if invoice.outstanding_amount > 0:
				if invoice.outstanding_amount == invoice.grand_total:
					invoice.payment_status = "Unpaid"
				else:
					invoice.payment_status = "Partly Paid"
			
			invoice.flags.ignore_validate_update_after_submit = True
			invoice.save(ignore_permissions=True)
			
			frappe.logger().info(
				f"Sales Return {self.name}: Reversed outstanding for Lab Invoice {self.return_against}"
			)
		
		except Exception as e:
			frappe.log_error(
				message=frappe.get_traceback(),
				title=f"Sales Return Reversal Failed: {self.name}"
			)
