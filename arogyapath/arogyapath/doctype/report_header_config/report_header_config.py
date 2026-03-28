# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReportHeaderConfig(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		branch: DF.Link
		city_state_pin: DF.Data | None
		email: DF.Data | None
		lab_name: DF.Data
		logo: DF.AttachImage | None
		nabl_cert_number: DF.Data | None
		nabl_valid_upto: DF.Date | None
		phone: DF.Data | None
		tagline: DF.Data | None
		website: DF.Data | None
	# end: auto-generated types

	pass
