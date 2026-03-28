# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConsumptionEntryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		lot: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		quantity_used: DF.Float
		reagent: DF.Link
		reagent_name: DF.Data | None
		test: DF.Link | None
		unit_of_measure: DF.Data | None
	# end: auto-generated types

	pass
