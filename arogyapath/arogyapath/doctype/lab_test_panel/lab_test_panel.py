# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabTestPanel(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.panel_item.panel_item import PanelItem

		department: DF.Link | None
		description: DF.SmallText | None
		is_active: DF.Check
		panel_code: DF.Data
		panel_name: DF.Data
		panel_price: DF.Currency
		tests: DF.Table[PanelItem]
	# end: auto-generated types

	def validate(self):
		if self.panel_code:
			self.panel_code = self.panel_code.upper()
