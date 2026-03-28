# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ReagentConsumptionEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.consumption_entry_item.consumption_entry_item import ConsumptionEntryItem

		branch: DF.Link
		consumption_date: DF.Date
		department: DF.Link | None
		entered_by: DF.Link | None
		items: DF.Table[ConsumptionEntryItem]
		naming_series: DF.Literal["RCE-.YYYY.-.#####"]
		purpose: DF.Literal["Routine Testing", "QC Run", "Calibration", "Wastage", "Other"]
	# end: auto-generated types

	def before_insert(self):
		if not self.entered_by:
			self.entered_by = frappe.session.user

	def on_submit(self):
		"""Deduct quantities from Reagent Lots on submit"""
		self._deduct_lot_quantities()

	def on_cancel(self):
		"""Restore quantities on cancel"""
		self._restore_lot_quantities()

	def _deduct_lot_quantities(self):
		for item in self.items:
			lot = frappe.get_doc("Reagent Lot", item.lot)
			lot.quantity_remaining = flt(lot.quantity_remaining) - flt(item.quantity_used)
			if lot.quantity_remaining <= 0:
				lot.quantity_remaining = 0
				lot.status = "Consumed"
			lot.save(ignore_permissions=True)

	def _restore_lot_quantities(self):
		for item in self.items:
			lot = frappe.get_doc("Reagent Lot", item.lot)
			lot.quantity_remaining = flt(lot.quantity_remaining) + flt(item.quantity_used)
			if lot.status == "Consumed":
				lot.status = "Active"
			lot.save(ignore_permissions=True)
