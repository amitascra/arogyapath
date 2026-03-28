# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class QCResultItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		observed_value: DF.Float
		parameter: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		target_mean: DF.Float
		target_sd: DF.Float
		westgard_flag: DF.Literal["Pass", "1-2s Warning", "1-3s Reject", "2-2s Reject", "R-4s Reject", "4-1s Reject", "10x Reject"]
		z_score: DF.Float
	# end: auto-generated types

	pass
