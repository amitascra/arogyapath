# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NotificationTemplate(Document):
	def render(self, context: dict) -> str:
		"""Render message_body as a Jinja2 template with given context."""
		from frappe.utils.jinja import render_template

		return render_template(self.message_body, context)

	def render_subject(self, context: dict) -> str:
		"""Render subject line with Jinja2 (for email channel)."""
		if not self.subject:
			return ""
		from frappe.utils.jinja import render_template

		return render_template(self.subject, context)

	@staticmethod
	def get_template(event: str, channel: str):
		"""
		Return the active Notification Template for a given event and channel.
		Falls back to an 'All' channel template if no channel-specific one exists.
		"""
		name = frappe.db.get_value(
			"Notification Template",
			{"event": event, "channel": channel, "is_active": 1},
			"name",
		)
		if not name:
			name = frappe.db.get_value(
				"Notification Template",
				{"event": event, "channel": "All", "is_active": 1},
				"name",
			)
		if name:
			return frappe.get_doc("Notification Template", name)
		return None

	@staticmethod
	def get_all_templates(event: str) -> list:
		"""Return all active templates for an event across all channels."""
		names = frappe.get_all(
			"Notification Template",
			filters={"event": event, "is_active": 1},
			pluck="name",
		)
		return [frappe.get_doc("Notification Template", n) for n in names]
