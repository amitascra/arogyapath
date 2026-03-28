# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabReportTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		css_style: DF.Code | None
		department: DF.Link | None
		header_config: DF.Link | None
		jinja_template: DF.Code | None
		show_clinical_comment: DF.Check
		show_methodology: DF.Check
		show_reference_ranges: DF.Check
		template_name: DF.Data
		watermark_text: DF.Data | None
	# end: auto-generated types

	pass
