import frappe
from frappe.utils import getdate

def check_expiry(doc, method=None):
	"""Check reagent lot expiry"""
	if doc.expiry_date and getdate(doc.expiry_date) < getdate():
		doc.is_active = 0
		frappe.msgprint(f"Reagent lot {doc.name} has expired")
