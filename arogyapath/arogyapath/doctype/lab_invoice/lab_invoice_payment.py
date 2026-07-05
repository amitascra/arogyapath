# Copyright (c) 2026, ArogyaPath and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

@frappe.whitelist()
def get_payment_entry(lab_invoice_name, bank_account=None):
	"""
	Create Payment Entry for Lab Invoice
	Similar to ERPNext's get_payment_entry for Sales Invoice
	"""
	doc = frappe.get_doc("Lab Invoice", lab_invoice_name)
	
	if doc.docstatus != 1:
		frappe.throw(_("Lab Invoice must be submitted before creating payment entry"))
	
	if doc.outstanding_amount <= 0:
		frappe.throw(_("Lab Invoice is already fully paid"))
	
	# Get company from pathology lab
	company = frappe.db.get_value("Pathology Lab", doc.pathology_lab, "company")
	if not company:
		frappe.throw(_("Please set Company in Pathology Lab {0}").format(doc.pathology_lab))
	
	# Get default company bank account
	bank = frappe.db.get_value("Pathology Lab", doc.pathology_lab, "default_bank_account")
	
	# Get patient's receivable account
	patient_account = get_patient_receivable_account(company)
	
	# Create Payment Entry
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.company = company
	pe.posting_date = nowdate()
	pe.reference_date = nowdate()
	pe.party_type = "Customer"
	pe.party = doc.patient
	pe.party_name = doc.patient_name
	
	# Set accounts
	pe.paid_from = patient_account  # Debtors account
	pe.paid_to = bank  # Bank account
	pe.paid_from_account_currency = frappe.db.get_value("Account", patient_account, "account_currency")
	pe.paid_to_account_currency = frappe.db.get_value("Account", bank, "account_currency")
	
	# Set amounts
	pe.paid_amount = doc.outstanding_amount
	pe.received_amount = doc.outstanding_amount
	pe.source_exchange_rate = 1
	pe.target_exchange_rate = 1
	
	# Add reference to Lab Invoice
	pe.append("references", {
		"reference_doctype": "Lab Invoice",
		"reference_name": doc.name,
		"total_amount": doc.grand_total,
		"outstanding_amount": doc.outstanding_amount,
		"allocated_amount": doc.outstanding_amount
	})
	
	pe.setup_party_account_field()
	pe.set_missing_values()
	
	return pe


def get_default_bank_account(company, bank_account=None):
	"""Get default bank account for company"""
	if bank_account:
		return bank_account
	
	# Try to get default company bank account
	default_bank = frappe.db.get_value(
		"Bank Account",
		{"company": company, "is_default": 1, "is_company_account": 1},
		"account"
	)
	
	if default_bank:
		return default_bank
	
	# Fallback: get any cash/bank account
	cash_account = frappe.db.get_value(
		"Account",
		{
			"company": company,
			"account_type": ["in", ["Bank", "Cash"]],
			"is_group": 0
		},
		"name"
	)
	
	if not cash_account:
		frappe.throw(_("Please set a default Bank Account for company {0}").format(company))
	
	return cash_account


def get_patient_receivable_account(company):
	"""Get default receivable account for patients"""
	# Try to get Debtors account
	receivable_account = frappe.db.get_value(
		"Account",
		{
			"company": company,
			"account_type": "Receivable",
			"is_group": 0
		},
		"name"
	)
	
	if not receivable_account:
		frappe.throw(_("Please set a Receivable Account for company {0}").format(company))
	
	return receivable_account
