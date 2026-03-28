# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReferenceRange(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		age_from_days: DF.Int
		age_to_days: DF.Int
		critical_max: DF.Float
		critical_min: DF.Float
		gender: DF.Literal["Both", "Male", "Female"]
		normal_max: DF.Float
		normal_min: DF.Float
		normal_text: DF.Data | None
		parameter: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		unit: DF.Data | None
	# end: auto-generated types

	pass
