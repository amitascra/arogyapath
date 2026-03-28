# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TestParameter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		decimal_places: DF.Int
		parameter_code: DF.Data | None
		parameter_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		print_bold: DF.Check
		result_type: DF.Literal["Numeric", "Text", "Positive-Negative", "Multiple Choice"]
		sort_order: DF.Int
		sub_heading: DF.Data | None
		unit: DF.Data | None
	# end: auto-generated types

	pass
