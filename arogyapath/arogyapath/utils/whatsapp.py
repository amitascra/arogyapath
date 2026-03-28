import frappe
import requests

def send_whatsapp_message(mobile, message, attachment_url=None):
	"""Send WhatsApp message via configured provider"""
	settings = frappe.get_single("Lab Settings")
	
	if not settings.whatsapp_provider:
		frappe.log_error("WhatsApp provider not configured")
		return False
	
	# Implementation will be added based on provider
	return True
