# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, date_diff, today


class ReagentLot(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		branch: DF.Link
		days_to_expiry: DF.Int
		expiry_date: DF.Date
		lot_number: DF.Data
		manufacture_date: DF.Date | None
		naming_series: DF.Literal["RLOT-.YYYY.-.#####"]
		purchase_price: DF.Currency
		quantity_received: DF.Float
		quantity_remaining: DF.Float
		reagent: DF.Link
		reagent_name: DF.Data | None
		received_by: DF.Link | None
		received_date: DF.Date | None
		status: DF.Literal["Active", "Expired", "Consumed", "Rejected"]
		supplier: DF.Data | None
		unit_of_measure: DF.Data | None
	# end: auto-generated types

	def before_save(self):
		self.check_expiry()
		if not self.quantity_remaining:
			self.quantity_remaining = self.quantity_received

	def check_expiry(self):
		"""Update days_to_expiry and set status to Expired if past date"""
		if self.expiry_date:
			days = date_diff(self.expiry_date, today())
			self.days_to_expiry = days
			if days < 0 and self.status == "Active":
				self.status = "Expired"
