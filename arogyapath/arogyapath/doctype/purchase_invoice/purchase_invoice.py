# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, add_days
from arogyapath.arogyapath.utils.gst import is_interstate, get_tax_rates


class PurchaseInvoice(Document):
	def validate(self):
		"""Validate purchase invoice before saving"""
		self.set_missing_values()
		self.calculate_item_amounts()
		self.calculate_taxes()
		self.calculate_totals()
		self.calculate_tds()
		self.set_outstanding_amount()
	
	def on_submit(self):
		"""Actions on submission"""
		self.update_item_last_purchase_rate()
		self.set_outstanding_amount()
	
	def on_cancel(self):
		"""Actions on cancellation"""
		self.set_outstanding_amount()
	
	def set_missing_values(self):
		"""Fetch missing values from supplier and branch"""
		if self.supplier:
			supplier = frappe.get_cached_doc("Supplier", self.supplier)
			
			# Set supplier name
			self.supplier_name = supplier.supplier_name
			
			# Set payment terms and due date
			if not self.payment_terms:
				self.payment_terms = supplier.payment_terms
			
			if not self.due_date and supplier.credit_days:
				self.due_date = add_days(self.posting_date, supplier.credit_days)
			
			# Set TDS details
			if supplier.tax_withholding_category:
				self.tds_applicable = 1
				self.tds_category = supplier.tax_withholding_category
				
				# Set TDS rate based on category
				tds_rates = {
					"194C - Contractor": 1.0,
					"194J - Professional Services": 10.0,
					"194H - Commission": 5.0,
					"194I - Rent": 10.0
				}
				self.tds_rate = tds_rates.get(supplier.tax_withholding_category, 0)
		
		# Determine if interstate
		if self.branch and self.supplier:
			branch_gstin = frappe.db.get_value("Lab Branch", self.branch, "gstin")
			supplier_gstin = frappe.db.get_value("Supplier", self.supplier, "gstin")
			
			if branch_gstin and supplier_gstin:
				self.is_interstate = is_interstate(branch_gstin, supplier_gstin)
	
	def calculate_item_amounts(self):
		"""Calculate amount for each item"""
		for item in self.items:
			# Basic amount = qty * rate
			item.amount = flt(item.qty) * flt(item.rate)
			
			# Get tax rates (18% for most items, can be customized)
			if not item.cgst_rate and not item.sgst_rate and not item.igst_rate:
				# Default 18% GST
				if self.is_interstate:
					item.igst_rate = 18.0
					item.cgst_rate = 0
					item.sgst_rate = 0
				else:
					item.cgst_rate = 9.0
					item.sgst_rate = 9.0
					item.igst_rate = 0
			
			# Calculate tax amounts
			item.cgst_amount = flt(item.amount * item.cgst_rate / 100, 2)
			item.sgst_amount = flt(item.amount * item.sgst_rate / 100, 2)
			item.igst_amount = flt(item.amount * item.igst_rate / 100, 2)
			
			# Total amount including tax
			item.total_amount = (
				flt(item.amount) + 
				flt(item.cgst_amount) + 
				flt(item.sgst_amount) + 
				flt(item.igst_amount)
			)
	
	def calculate_taxes(self):
		"""Calculate total taxes"""
		self.total_cgst = sum(flt(d.cgst_amount) for d in self.items)
		self.total_sgst = sum(flt(d.sgst_amount) for d in self.items)
		self.total_igst = sum(flt(d.igst_amount) for d in self.items)
		self.total_tax = self.total_cgst + self.total_sgst + self.total_igst
	
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
	
	def calculate_tds(self):
		"""Calculate TDS amount"""
		if self.tds_applicable and self.tds_rate:
			# TDS is calculated on base total (before tax)
			self.tds_amount = flt(self.base_total * self.tds_rate / 100, 2)
		else:
			self.tds_amount = 0
	
	def set_outstanding_amount(self):
		"""Set outstanding amount"""
		if self.docstatus == 0:
			# Draft - outstanding = grand total
			self.outstanding_amount = self.grand_total
		elif self.docstatus == 1:
			# Submitted - calculate from payments
			paid_amount = self.get_total_paid_amount()
			self.outstanding_amount = flt(self.grand_total) - flt(paid_amount)
			
			# Update payment status
			if self.outstanding_amount <= 0:
				self.payment_status = "Paid"
			elif paid_amount > 0:
				self.payment_status = "Partly Paid"
			else:
				self.payment_status = "Unpaid"
		elif self.docstatus == 2:
			# Cancelled - no outstanding
			self.outstanding_amount = 0
			self.payment_status = "Cancelled"
	
	def get_total_paid_amount(self):
		"""Get total amount paid via Payment Entry"""
		paid_amount = frappe.db.sql("""
			SELECT SUM(per.allocated_amount)
			FROM `tabPayment Entry Reference` per
			INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
			WHERE per.reference_doctype = 'Purchase Invoice'
				AND per.reference_name = %s
				AND pe.docstatus = 1
		""", self.name)
		
		return flt(paid_amount[0][0]) if paid_amount else 0
	
	def update_item_last_purchase_rate(self):
		"""Update last purchase rate in Item master"""
		for item_row in self.items:
			if item_row.item:
				frappe.db.set_value(
					"Item", 
					item_row.item, 
					"last_purchase_rate", 
					item_row.rate
				)
