# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class WestgardRuleConfig(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		analyzer: DF.Link | None
		department: DF.Link
		enable_10x: DF.Check
		enable_1_2s: DF.Check
		enable_1_3s: DF.Check
		enable_2_2s: DF.Check
		enable_4_1s: DF.Check
		enable_r_4s: DF.Check
		naming_series: DF.Literal["WRC-.YYYY.-.####"]
		reject_action: DF.Literal["Hold Results", "Notify Pathologist", "Both"]
		warning_action: DF.Literal["Notify Technician", "Notify Pathologist", "Both", "None"]
	# end: auto-generated types

	pass
