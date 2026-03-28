# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabOrderItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		department: DF.Link | None
		is_outsourced: DF.Check
		panel: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		rate: DF.Currency
		result: DF.Link | None
		sample_type: DF.Link | None
		status: DF.Literal["Pending", "Processing", "Resulted", "Outsourced", "Cancelled"]
		tat_deadline: DF.Datetime | None
		test: DF.Link | None
		test_name: DF.Data | None
	# end: auto-generated types

	pass
