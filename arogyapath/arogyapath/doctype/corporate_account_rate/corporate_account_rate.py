# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CorporateAccountRate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		gst_applicable: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rate: DF.Currency
		test: DF.Link
		test_name: DF.Data | None
	# end: auto-generated types

	pass
