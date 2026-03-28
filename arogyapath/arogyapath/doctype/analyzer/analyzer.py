# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Analyzer(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amc_expiry_date: DF.Date | None
		amc_vendor: DF.Data | None
		analyzer_code: DF.Data
		analyzer_name: DF.Data
		branch: DF.Link
		department: DF.Link
		installation_date: DF.Date | None
		is_active: DF.Check
		last_calibration_date: DF.Date | None
		manufacturer: DF.Data | None
		model_number: DF.Data | None
		next_calibration_due: DF.Date | None
		serial_number: DF.Data | None
	# end: auto-generated types

	pass
