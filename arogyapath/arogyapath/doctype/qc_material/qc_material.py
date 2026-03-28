# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class QCMaterial(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cv_percent: DF.Float
		department: DF.Link
		expiry_date: DF.Date | None
		is_active: DF.Check
		level: DF.Literal["Level 1 (Low)", "Level 2 (Normal)", "Level 3 (High)"]
		lot_number: DF.Data | None
		manufacturer: DF.Data | None
		material_code: DF.Data
		material_name: DF.Data
		target_mean: DF.Float
		target_sd: DF.Float
	# end: auto-generated types

	pass
