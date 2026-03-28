# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		auto_release_normal: DF.Check
		barcode_format: DF.Literal["Code128", "QR", "Code39"]
		critical_alert_mode: DF.Literal["", "WhatsApp", "SMS", "Both"]
		default_branch: DF.Link | None
		default_gst_rate: DF.Float
		default_sac_code: DF.Data | None
		default_tat_hours: DF.Int
		fiscal_year_start: DF.Literal["April", "January"]
		invoice_prefix: DF.Data | None
		report_portal_url: DF.Data | None
		sms_api_key: DF.Password | None
		sms_provider: DF.Literal["", "MSG91", "Fast2SMS", "Twilio"]
		whatsapp_api_key: DF.Password | None
		whatsapp_phone_id: DF.Data | None
		whatsapp_provider: DF.Literal["", "Meta Cloud API", "Twilio", "MSG91"]
	# end: auto-generated types

	pass
