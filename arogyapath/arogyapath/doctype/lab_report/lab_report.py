# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
import secrets
from frappe.model.document import Document


class LabReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link | None
		delivered_to: DF.Data | None
		delivery_status: DF.Literal["Pending", "WhatsApp Sent", "Email Sent", "Printed", "Delivered"]
		email_sent_at: DF.Datetime | None
		lab_order: DF.Link
		naming_series: DF.Literal["RPT-.BRANCH.-.YYYY.-.#####"]
		patient: DF.Link | None
		patient_name: DF.Data | None
		pdf_attachment: DF.Attach | None
		qr_code: DF.AttachImage | None
		report_date: DF.Date
		report_template: DF.Link | None
		report_url_token: DF.Data | None
		signed_by: DF.Link | None
		whatsapp_sent_at: DF.Datetime | None
	# end: auto-generated types

	def before_insert(self):
		"""Generate unique token for public report access"""
		if not self.report_url_token:
			self.report_url_token = secrets.token_urlsafe(16)

	def after_insert(self):
		"""Generate QR code after insert so we have the doc name"""
		self.generate_qr_code()

	def generate_qr_code(self):
		"""Generate QR code pointing to patient portal URL"""
		try:
			settings = frappe.get_single("Lab Settings")
			base_url = settings.report_portal_url or frappe.utils.get_url()
			report_url = f"{base_url}/report/{self.report_url_token}"

			from arogyapath.arogyapath.utils.barcode import generate_qr_code
			qr_data = generate_qr_code(report_url)

			if qr_data:
				file_doc = frappe.get_doc({
					"doctype": "File",
					"file_name": f"qr_{self.name}.png",
					"attached_to_doctype": self.doctype,
					"attached_to_name": self.name,
					"attached_to_field": "qr_code",
					"content": qr_data,
					"is_private": 0
				})
				file_doc.insert(ignore_permissions=True)
				self.db_set("qr_code", file_doc.file_url)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "QR Code Generation Failed")

	def send_whatsapp(self):
		"""Send report via WhatsApp"""
		try:
			patient = frappe.get_doc("Patient", self.patient)
			if not patient.mobile:
				frappe.throw("Patient mobile number not set")

			settings = frappe.get_single("Lab Settings")
			base_url = settings.report_portal_url or frappe.utils.get_url()
			report_url = f"{base_url}/report/{self.report_url_token}"

			message = f"Dear {patient.full_name},\n\nYour lab report is ready. View it at: {report_url}\n\nThank you."

			from arogyapath.arogyapath.utils.whatsapp import send_whatsapp_message
			success = send_whatsapp_message(patient.mobile, message, self.pdf_attachment)

			if success:
				self.db_set("delivery_status", "WhatsApp Sent")
				self.db_set("whatsapp_sent_at", frappe.utils.now_datetime())
				self.db_set("delivered_to", patient.mobile)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "WhatsApp Delivery Failed")
