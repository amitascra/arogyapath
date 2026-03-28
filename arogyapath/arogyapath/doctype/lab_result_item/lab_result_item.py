# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabResultItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		critical_max: DF.Float
		critical_min: DF.Float
		flag: DF.Literal["Normal", "Low", "High", "Critical Low", "Critical High", "Abnormal"]
		instrument: DF.Data | None
		method: DF.Data | None
		normal_max: DF.Float
		normal_min: DF.Float
		parameter_code: DF.Data | None
		parameter_name: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		reference_range_text: DF.Data | None
		result_numeric: DF.Float
		result_value: DF.Data | None
		unit: DF.Data | None
	# end: auto-generated types

	pass
