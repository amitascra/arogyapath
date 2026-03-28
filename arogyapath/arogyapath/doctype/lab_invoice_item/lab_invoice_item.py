# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabInvoiceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		cgst_rate: DF.Float
		department: DF.Link | None
		discount_amount: DF.Currency
		hsn_sac_code: DF.Data | None
		igst_rate: DF.Float
		is_gst_exempt: DF.Check
		mrp: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rate: DF.Currency
		sgst_rate: DF.Float
		tax_amount: DF.Currency
		taxable_amount: DF.Currency
		test: DF.Link
		test_name: DF.Data | None
	# end: auto-generated types

	pass
