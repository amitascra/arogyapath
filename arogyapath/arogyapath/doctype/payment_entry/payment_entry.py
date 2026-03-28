# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class PaymentEntry(Document):
	def validate(self):
		"""Validate payment entry before saving"""
		self.validate_party()
		self.set_missing_values()
		self.validate_allocated_amount()
		self.set_amounts()
		self.validate_difference_amount()
		self.set_status()
	
	def before_submit(self):
		"""Validate before submission"""
		if abs(self.difference_amount) > 0.01:
			frappe.throw(_("Difference amount must be zero before submitting"))
	
	def on_submit(self):
		"""Update outstanding amounts on submission"""
		self.update_outstanding_amounts()
		self.set_status()
	
	def on_cancel(self):
		"""Reverse outstanding amounts on cancellation"""
		self.reverse_outstanding_amounts()
		self.set_status()
	
	def validate_party(self):
		"""Validate party details"""
		if self.payment_type == "Internal Transfer":
			# Internal transfers don't need party
			self.party_type = None
			self.party = None
			self.party_name = None
			return
		
		if not self.party_type:
			frappe.throw(_("Party Type is mandatory"))
		
		if not self.party:
			frappe.throw(_("Party is mandatory"))
		
		# Check if party exists
		if not frappe.db.exists(self.party_type, self.party):
			frappe.throw(_("{0} {1} does not exist").format(
				_(self.party_type), self.party
			))
	
	def set_missing_values(self):
		"""Fetch party name and other missing values"""
		if self.party_type and self.party:
			# Fetch party name based on party type
			if self.party_type == "Patient":
				self.party_name = frappe.db.get_value("Patient", self.party, "full_name")
			elif self.party_type == "Supplier":
				self.party_name = frappe.db.get_value("Supplier", self.party, "supplier_name")
			elif self.party_type == "Doctor":
				self.party_name = frappe.db.get_value("Doctor", self.party, "doctor_name")
			elif self.party_type == "Employee":
				self.party_name = frappe.db.get_value("Employee", self.party, "employee_name")
			elif self.party_type == "Corporate Account":
				self.party_name = frappe.db.get_value("Corporate Account", self.party, "account_name")
		
		# Fetch outstanding amounts for references
		for ref in self.references:
			if ref.reference_doctype and ref.reference_name:
				doc = frappe.get_doc(ref.reference_doctype, ref.reference_name)
				
				# Set total amount
				if hasattr(doc, 'grand_total'):
					ref.total_amount = doc.grand_total
				elif hasattr(doc, 'total_amount'):
					ref.total_amount = doc.total_amount
				
				# Set outstanding amount
				if hasattr(doc, 'outstanding_amount'):
					ref.outstanding_amount = doc.outstanding_amount
				else:
					ref.outstanding_amount = ref.total_amount
	
	def validate_allocated_amount(self):
		"""Ensure allocated amount doesn't exceed outstanding"""
		for ref in self.references:
			if not ref.allocated_amount:
				continue
			
			if flt(ref.allocated_amount) > flt(ref.outstanding_amount):
				frappe.throw(
					_("Row #{0}: Allocated amount cannot exceed outstanding amount").format(ref.idx)
				)
	
	def set_amounts(self):
		"""Calculate total allocated, unallocated, and difference amounts"""
		# Total allocated from references
		self.total_allocated_amount = sum(
			flt(d.allocated_amount) for d in self.references
		)
		
		# Total deductions (bank charges, TDS)
		total_deductions = sum(
			flt(d.amount) for d in self.deductions
		)
		
		# Unallocated = paid - allocated - deductions
		self.unallocated_amount = (
			flt(self.paid_amount) - 
			flt(self.total_allocated_amount) - 
			total_deductions
		)
		
		# Difference = received - paid (exchange rate difference or rounding)
		self.difference_amount = flt(self.received_amount) - flt(self.paid_amount)
	
	def validate_difference_amount(self):
		"""Difference must be zero on submit"""
		if self.docstatus == 1 and abs(flt(self.difference_amount)) > 0.01:
			frappe.throw(_("Difference amount must be zero before submitting"))
	
	def set_status(self):
		"""Set payment status"""
		if self.docstatus == 0:
			self.status = "Draft"
		elif self.docstatus == 1:
			if self.clearance_date:
				self.status = "Cleared"
			else:
				self.status = "Submitted"
		elif self.docstatus == 2:
			self.status = "Cancelled"
	
	def update_outstanding_amounts(self):
		"""Update outstanding in referenced documents"""
		for ref in self.references:
			if not ref.allocated_amount:
				continue
			
			try:
				doc = frappe.get_doc(ref.reference_doctype, ref.reference_name)
				
				# Update outstanding amount
				if hasattr(doc, 'outstanding_amount'):
					doc.outstanding_amount = flt(doc.outstanding_amount) - flt(ref.allocated_amount)
					
					# Update payment status
					if hasattr(doc, 'payment_status'):
						if doc.outstanding_amount <= 0:
							doc.payment_status = "Paid"
						elif doc.outstanding_amount < doc.grand_total:
							doc.payment_status = "Partly Paid"
						else:
							doc.payment_status = "Unpaid"
					
					doc.flags.ignore_validate_update_after_submit = True
					doc.save(ignore_permissions=True)
					
					frappe.logger().info(
						f"Payment Entry {self.name}: Updated outstanding for {ref.reference_doctype} {ref.reference_name}"
					)
			
			except Exception as e:
				frappe.log_error(
					message=frappe.get_traceback(),
					title=f"Payment Entry Outstanding Update Failed: {self.name}"
				)
				frappe.throw(
					_("Failed to update outstanding for {0} {1}. Error: {2}").format(
						ref.reference_doctype, ref.reference_name, str(e)
					)
				)
	
	def reverse_outstanding_amounts(self):
		"""Reverse outstanding updates on cancellation"""
		for ref in self.references:
			if not ref.allocated_amount:
				continue
			
			try:
				doc = frappe.get_doc(ref.reference_doctype, ref.reference_name)
				
				# Reverse outstanding amount
				if hasattr(doc, 'outstanding_amount'):
					doc.outstanding_amount = flt(doc.outstanding_amount) + flt(ref.allocated_amount)
					
					# Update payment status
					if hasattr(doc, 'payment_status'):
						if doc.outstanding_amount > 0:
							if doc.outstanding_amount == doc.grand_total:
								doc.payment_status = "Unpaid"
							else:
								doc.payment_status = "Partly Paid"
					
					doc.flags.ignore_validate_update_after_submit = True
					doc.save(ignore_permissions=True)
					
					frappe.logger().info(
						f"Payment Entry {self.name}: Reversed outstanding for {ref.reference_doctype} {ref.reference_name}"
					)
			
			except Exception as e:
				frappe.log_error(
					message=frappe.get_traceback(),
					title=f"Payment Entry Reversal Failed: {self.name}"
				)
