# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt as _flt, today


class LabInvoice(Document):
	def validate(self):
		self._set_gst_details()
		self._validate_gstin()
		self._set_item_amounts()
		self._apply_corporate_rates()
		self._apply_discount_scheme()
		self._compute_gst()
		self._compute_doctor_commission()
		self._update_payment_status()

	def _set_gst_details(self):
		"""Set GST details from patient/corporate and lab branch"""
		# Get lab GSTIN from branch
		if self.branch:
			branch = frappe.get_cached_doc("Lab Branch", self.branch)
			self.company_gstin = branch.gstin or ""
		else:
			self.company_gstin = ""
		
		# Get patient/corporate GST details
		if self.corporate_account:
			# B2B - get from corporate account
			corp = frappe.get_cached_doc("Corporate Account", self.corporate_account)
			self.patient_gstin = corp.gstin or ""
			self.billing_address_gstin = corp.gstin or ""
			# Set GST category based on GSTIN
			self.gst_category = self._guess_gst_category(self.patient_gstin)
		else:
			# B2C - individual patient
			self.gst_category = "Unregistered"
			self.patient_gstin = ""
			self.billing_address_gstin = ""
		
		# Calculate place of supply
		self.place_of_supply = self._get_place_of_supply()
		
		# Determine if interstate
		self.is_interstate = self._is_interstate()
		
		# Set tax category and template
		self._set_tax_template()

	def _guess_gst_category(self, gstin):
		"""Guess GST category from GSTIN"""
		if not gstin or len(gstin) != 15:
			return "Unregistered"
		
		# Check if GSTIN starts with state code
		if gstin[:2].isdigit():
			return "Registered Regular"
		
		return "Unregistered"

	def _get_place_of_supply(self):
		"""Calculate place of supply"""
		if self.gst_category in ("Overseas", "SEZ"):
			return "96-Other Countries"
		
		# For unregistered, use lab state
		if self.gst_category == "Unregistered":
			if self.company_gstin and len(self.company_gstin) >= 2:
				state_code = self.company_gstin[:2]
				state_name = self._get_state_name(state_code)
				return f"{state_code}-{state_name}"
		
		# For registered, use customer state
		if self.patient_gstin and len(self.patient_gstin) >= 2:
			state_code = self.patient_gstin[:2]
			state_name = self._get_state_name(state_code)
			return f"{state_code}-{state_name}"
		
		return ""

	def _get_state_name(self, state_code):
		"""Get state name from state code"""
		states = {
			"09": "Uttar Pradesh",
			"27": "Maharashtra",
			"07": "Delhi",
			"29": "Rajasthan",
			"05": "Uttarakhand",
			"10": "Bihar",
			"32": "Kerala",
			"33": "Tamil Nadu",
			"19": "West Bengal",
			"12": "Arunachal Pradesh",
			"13": "Assam",
			"22": "Chhattisgarh",
			"30": "Goa",
			"24": "Gujarat",
			"06": "Haryana",
			"02": "Himachal Pradesh",
			"01": "Jammu & Kashmir",
			"20": "Jharkhand",
			"31": "Karnataka",
			"23": "Madhya Pradesh",
			"16": "Manipur",
			"14": "Meghalaya",
			"17": "Mizoram",
			"15": "Nagaland",
			"21": "Odisha",
			"34": "Pondicherry",
			"03": "Punjab",
			"08": "Rajasthan",
			"11": "Sikkim",
			"36": "Telangana",
			"37": "Andhra Pradesh",
			"28": "Andhra Pradesh",
			"35": "Andaman & Nicobar Islands",
			"04": "Chandigarh",
			"26": "Dadra & Nagar Haveli",
			"25": "Daman & Diu",
			"31": "Lakshadweep"
		}
		return states.get(state_code, "Unknown")

	def _is_interstate(self):
		"""Check if transaction is interstate"""
		if not self.company_gstin or not self.place_of_supply:
			return False
		
		lab_state = self.company_gstin[:2]
		supply_state = self.place_of_supply[:2]
		
		return lab_state != supply_state

	def _set_tax_template(self):
		"""Set tax category and template based on GST details"""
		# Clear existing if GST not applicable
		if self.gst_category in ("Unregistered", "SEZ", "Overseas"):
			self.tax_category = ""
			self.taxes_and_charges = ""
			return
		
		# Get default pathology lab
		from arogyapath.arogyapath.seed_chart_of_accounts import get_default_lab
		default_lab = get_default_lab()
		if not default_lab:
			return
		
		# Try to find template by tax category
		if self.is_interstate:
			category_name = "Out of State GST"
		else:
			category_name = "In State GST"
		
		# Get tax category
		tax_category = frappe.db.exists("Tax Category", {
			"category_name": category_name,
			"is_inter_state": 1 if self.is_interstate else 0,
			"disabled": 0
		})
		
		if tax_category:
			self.tax_category = tax_category
			# Get template for this category
			template = frappe.db.exists("Sales Taxes and Charges Template", {
				"pathology_lab": default_lab,
				"tax_category": tax_category,
				"disabled": 0
			})
			if template:
				self.taxes_and_charges = template
		else:
			# Fallback to default template
			template = frappe.db.exists("Sales Taxes and Charges Template", {
				"pathology_lab": default_lab,
				"is_default": 1,
				"disabled": 0
			})
			if template:
				self.taxes_and_charges = template

	def _validate_gstin(self):
		"""Validate patient GSTIN format if provided."""
		from arogyapath.arogyapath.utils.gst import validate_gstin

		validate_gstin(self.patient_gstin, "Patient GSTIN")
		if self.branch:
			lab_gstin = frappe.db.get_value("Lab Branch", self.branch, "gstin")
			validate_gstin(lab_gstin, "Lab GSTIN")

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
