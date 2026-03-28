# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CollectionCenter(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.SmallText | None
		branch: DF.Link
		center_code: DF.Data | None
		center_name: DF.Data
		contact_mobile: DF.Data | None
		contact_person: DF.Data | None
		is_active: DF.Check
	# end: auto-generated types

	pass
