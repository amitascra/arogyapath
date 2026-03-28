# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CorporateAccount(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.corporate_account_rate.corporate_account_rate import CorporateAccountRate

		billing_address: DF.SmallText | None
		company_code: DF.Data | None
		company_name: DF.Data
		contact_email: DF.Data | None
		contact_mobile: DF.Data | None
		contact_person: DF.Data | None
		credit_days: DF.Int
		credit_limit: DF.Currency
		custom_rates: DF.Table[CorporateAccountRate]
		gstin: DF.Data | None
		is_active: DF.Check
	# end: auto-generated types

	def validate(self):
		if self.gstin:
			from arogyapath.arogyapath.utils.gst import validate_gstin
			validate_gstin(self.gstin)

	def get_test_rate(self, test_code):
		"""Return corporate rate for a test, fallback to MRP"""
		for row in self.custom_rates:
			if row.test == test_code:
				return row.rate
		return frappe.db.get_value("Lab Test Master", test_code, "cost")
