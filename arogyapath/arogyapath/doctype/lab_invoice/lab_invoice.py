# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt
#
# GST architecture follows ERPNext / India Compliance pattern:
#   - GSTIN lives on Address DocType (custom fields added by custom_fields.py)
#   - billing_address_gstin / gst_category / company_gstin are ALL fetched
#     from their linked Address documents via Frappe's fetch_from mechanism
#   - This controller only resolves place_of_supply and picks the right
#     Sales Taxes and Charges Template — it does NOT re-read GSTIN directly

import frappe
from frappe.model.document import Document
from frappe.utils import flt as _flt


class LabInvoice(Document):
	def validate(self):
		self._resolve_company_address()
		self._set_place_of_supply()
		self._auto_set_tax_template()
		self._validate_gstin()
		self._set_item_amounts()
		self._apply_corporate_rates()
		self._apply_discount_scheme()
		self._compute_gst()
		self._compute_doctor_commission()
		self._update_payment_status()
		self.set_status()
	
	def on_submit(self):
		"""Handle invoice submission"""
		self.set_status(update=True)
	
	def on_cancel(self):
		"""Handle invoice cancellation"""
		self.set_status(update=True)
	
	def set_status(self, update=False):
		"""Set payment status based on outstanding amount (similar to ERPNext Sales Invoice)"""
		if self.docstatus == 2:
			self.status = "Cancelled"
		elif self.docstatus == 1:
			outstanding = _flt(self.outstanding_amount, 2)
			grand_total = _flt(self.grand_total, 2)
			
			if outstanding <= 0:
				self.status = "Paid"
				self.payment_status = "Paid"
			elif 0 < outstanding < grand_total:
				self.status = "Partly Paid"
				self.payment_status = "Partly Paid"
			else:
				self.status = "Unpaid"
				self.payment_status = "Unpaid"
		else:
			self.status = "Draft"
			self.payment_status = "Unpaid"
		
		if update:
			frappe.db.set_value("Lab Invoice", self.name, {
				"status": self.status,
				"payment_status": self.payment_status
			}, update_modified=False)

	# ── Address resolution ─────────────────────────────────────────────────

	def _resolve_company_address(self):
		"""
		Auto-populate company_address from the linked Lab Branch.
		company_gstin is then fetched automatically by fetch_from on
		the company_address field (custom field).
		"""
		if not self.branch:
			return
		branch_address = frappe.db.get_value("Lab Branch", self.branch, "branch_address")
		if branch_address and not self.get("company_address"):
			self.company_address = branch_address

	# ── Place of Supply ────────────────────────────────────────────────────

	def _set_place_of_supply(self):
		"""
		Derive place of supply using gst.py helper.
		Uses billing_address_gstin (fetched from customer_address) and
		company_gstin (fetched from company_address / branch_address).
		"""
		if self.get("place_of_supply"):
			return  # already set by user or JS

		from arogyapath.arogyapath.utils.gst import get_place_of_supply
		self.place_of_supply = get_place_of_supply(self)

	# ── Tax Template ───────────────────────────────────────────────────────

	def _auto_set_tax_template(self):
		"""
		Auto-select the Sales Taxes and Charges Template only when
		taxes_and_charges is not already set by the user.

		Mirrors India Compliance's get_tax_template_based_on_category() +
		get_tax_template() — scoped to Pathology Lab instead of Company.
		"""
		from arogyapath.arogyapath.utils.gst import (
			GST_EXEMPT_CATEGORIES,
			get_tax_template_for_invoice,
			populate_taxes_from_template,
		)

		# GST category is fetched from customer_address via fetch_from.
		# Fall back to Unregistered if not yet populated.
		gst_category = (self.get("gst_category") or "Unregistered").strip()

		if gst_category in GST_EXEMPT_CATEGORIES:
			# Bill of Supply — no tax template needed
			self.taxes_and_charges = ""
			self.taxes = []
			return

		# Only auto-fill if not already set
		if not self.get("taxes_and_charges"):
			self.taxes_and_charges = get_tax_template_for_invoice(self)

		# Always (re)populate taxes rows from template
		if self.get("taxes_and_charges"):
			populate_taxes_from_template(self)

	# ── GSTIN validation ───────────────────────────────────────────────────

	def _validate_gstin(self):
		"""
		Validate GSTINs that are now stored on Address and fetched here.
		billing_address_gstin comes from customer_address.gstin via fetch_from.
		company_gstin comes from company_address.gstin via fetch_from.
		"""
		from arogyapath.arogyapath.utils.gst import validate_gstin

		validate_gstin(self.get("billing_address_gstin") or "", "Billing GSTIN")
		validate_gstin(self.get("company_gstin") or "", "Lab GSTIN")

	def _set_item_amounts(self):
		"""Compute rate = amount for each line item (lab tests are qty 1)."""
		for item in self.items:
			item.amount = _flt(item.rate, 2)
			if not item.hsn_sac_code:
				item.hsn_sac_code = "999316"

	def _apply_corporate_rates(self):
		"""Apply custom rates from Corporate Account rate list if set."""
		if not self.corporate_account:
			return
		try:
			corp = frappe.get_doc("Corporate Account", self.corporate_account)
			rate_map = {r.test: r.rate for r in corp.get("rate_list", [])}
			for item in self.items:
				if item.test in rate_map:
					item.rate = _flt(rate_map[item.test], 2)
					item.amount = _flt(item.rate, 2)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "ArogyaPath: _apply_corporate_rates failed")

	def _apply_discount_scheme(self):
		"""Apply discount scheme."""
		if not self.discount_scheme:
			self.discount_amount = 0.0
			return

		if False:  # Placeholder for future manual discount feature
			total_gross = sum(_flt(i.amount) for i in self.items)
			self.discount_amount = _flt(total_gross * _flt(self.manual_discount_pct) / 100, 2)
			return

		scheme = frappe.get_doc("Discount Scheme", self.discount_scheme)
		if not scheme.is_active:
			self.discount_amount = 0.0
			return

		total_gross = sum(_flt(i.amount) for i in self.items)
		if scheme.discount_type == "Percentage":
			self.discount_amount = _flt(total_gross * _flt(scheme.discount_value) / 100, 2)
		else:
			self.discount_amount = _flt(scheme.discount_value, 2)

	def _compute_gst(self):
		"""
		Delegate all GST computation to gst.py which sets:
		gross_amount, taxable_amount, cgst_amount, sgst_amount,
		igst_amount, total_tax, grand_total, outstanding_amount
		on the invoice and individual rate/amount fields on items.
		"""
		from arogyapath.arogyapath.utils.gst import compute_invoice_taxes

		compute_invoice_taxes(self)

	def _compute_doctor_commission(self):
		"""Compute doctor commission using gst.py helper."""
		from arogyapath.arogyapath.utils.gst import compute_doctor_commission

		if not self.referred_by:
			self.commission_amount = 0.0
			self.commission_rate = 0.0
			return

		doctor = frappe.get_cached_doc("Doctor", self.referred_by)
		self.commission_rate = _flt(doctor.commission_rate)
		self.commission_on = doctor.commission_on or "Net"

		if doctor.commission_type == "Fixed Per Test":
			self.commission_amount = _flt(len(self.items) * _flt(doctor.commission_rate), 2)
		else:
			compute_doctor_commission(self)

	def _update_payment_status(self):
		"""Set outstanding and payment_status based on Payment Entry allocations."""
		if self.docstatus == 0:
			# Draft - outstanding = grand total
			self.outstanding_amount = self.grand_total
			self.payment_status = "Unpaid"
		elif self.docstatus == 1:
			# Submitted - calculate from Payment Entry
			paid_amount = self.get_total_paid_amount()
			self.outstanding_amount = _flt(self.grand_total) - _flt(paid_amount)
			
			# Update payment status
			if self.outstanding_amount <= 0:
				self.payment_status = "Paid"
			elif paid_amount > 0:
				self.payment_status = "Partly Paid"
			else:
				self.payment_status = "Unpaid"
		elif self.docstatus == 2:
			# Cancelled
			self.outstanding_amount = 0
			self.payment_status = "Cancelled"
	
	def get_total_paid_amount(self):
		"""Get total amount paid via Payment Entry"""
		paid_amount = frappe.db.sql("""
			SELECT SUM(per.allocated_amount)
			FROM `tabPayment Entry Reference` per
			INNER JOIN `tabPayment Entry` pe ON per.parent = pe.name
			WHERE per.reference_doctype = 'Lab Invoice'
				AND per.reference_name = %s
				AND pe.docstatus = 1
		""", self.name)
		
		return _flt(paid_amount[0][0]) if paid_amount else 0

	def on_submit(self):
		"""Set initial outstanding on submit"""
		self.outstanding_amount = self.grand_total
		self.payment_status = "Unpaid"
		if self.lab_order:
			frappe.db.set_value("Lab Order", self.lab_order, "invoice", self.name)
		self._send_invoice_notification()

	def on_cancel(self):
		"""Clear outstanding on cancel"""
		self.outstanding_amount = 0
		self.payment_status = "Cancelled"
		if self.lab_order:
			frappe.db.set_value("Lab Order", self.lab_order, "invoice", None)

	def _send_invoice_notification(self):
		"""Send invoice notification via WhatsApp/SMS after submit."""
		try:
			from arogyapath.arogyapath.doctype.notification_template.notification_template import NotificationTemplate

			template = NotificationTemplate.get_template("Invoice Created", "WhatsApp")
			if not template:
				return
			patient = frappe.get_cached_doc("Patient", self.patient) if self.patient else None
			if not patient or not patient.mobile:
				return
			context = {
				"patient_name": patient.full_name,
				"invoice_number": self.name,
				"grand_total": self.grand_total,
				"due_date": self.due_date,
				"branch_name": self.branch,
				"payment_link": self.payment_link or "",
			}
			template.render(context)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "ArogyaPath: Invoice notification failed")
