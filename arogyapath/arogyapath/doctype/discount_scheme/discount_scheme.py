# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DiscountScheme(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		applicable_to: DF.Literal["All Tests", "Specific Department", "Specific Tests"]
		department: DF.Link | None
		discount_type: DF.Literal["Percentage", "Fixed Amount"]
		discount_value: DF.Float
		is_active: DF.Check
		scheme_name: DF.Data
		valid_from: DF.Date | None
		valid_to: DF.Date | None
	# end: auto-generated types

	pass
