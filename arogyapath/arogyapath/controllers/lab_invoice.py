import frappe
from arogyapath.arogyapath.utils.gst import compute_invoice_taxes, validate_gstin

def validate(doc, method=None):
	"""Validate Lab Invoice"""
	validate_gstin(doc.patient_gstin)
	compute_invoice_taxes(doc)
	compute_doctor_commission(doc)

def on_submit(doc, method=None):
	"""Handle invoice submission"""
	if doc.payment_mode == "Online":
		create_payment_link(doc)
	send_invoice_notification(doc)

def compute_doctor_commission(doc):
	"""Calculate doctor commission"""
	if not doc.referred_by:
		return
	
	doctor = frappe.get_doc("Doctor", doc.referred_by)
	if doctor.commission_type == "None":
		return
	
	base_amount = doc.taxable_amount if doctor.commission_on == "Net" else doc.gross_amount
	
	if doctor.commission_type == "Percentage":
		doc.commission_amount = base_amount * doctor.commission_rate / 100
	elif doctor.commission_type == "Fixed Per Test":
		doc.commission_amount = len(doc.items) * doctor.commission_rate

def create_payment_link(doc):
	"""Create payment link using frappe/payments"""
	pass

def send_invoice_notification(doc):
	"""Send invoice notification"""
	pass
