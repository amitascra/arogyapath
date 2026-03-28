# Copyright (c) 2026, Amit Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class DoctorCommissionLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from arogyapath.arogyapath.doctype.commission_log_item.commission_log_item import CommissionLogItem

		branch: DF.Link | None
		doctor: DF.Link
		items: DF.Table[CommissionLogItem]
		naming_series: DF.Literal["DCL-.YYYY.-.#####"]
		net_payable: DF.Currency
		payment_reference: DF.Data | None
		period_from: DF.Date
		period_to: DF.Date
		settlement_date: DF.Date | None
		settlement_frequency: DF.Literal["Monthly", "Quarterly"]
		status: DF.Literal["Draft", "Approved", "Settled"]
		tds_amount: DF.Currency
		tds_rate: DF.Float
		total_commission: DF.Currency
		total_invoiced: DF.Currency
	# end: auto-generated types

	def validate(self):
		self._compute_totals()

	def _compute_totals(self):
		self.total_invoiced = flt(sum(flt(i.grand_total) for i in self.items), 2)
		self.total_commission = flt(sum(flt(i.commission_amount) for i in self.items), 2)
		self.tds_amount = flt(self.total_commission * self.tds_rate / 100, 2)
		self.net_payable = flt(self.total_commission - self.tds_amount, 2)

	def on_update(self):
		"""Mark invoices as commission settled when status is Settled"""
		if self.status == "Settled":
			for item in self.items:
				frappe.db.set_value("Lab Invoice", item.lab_invoice, "commission_settled", 1)

	@frappe.whitelist()
	def fetch_unsettled_invoices(self):
		"""Fetch all unsettled invoices for this doctor in the period"""
		invoices = frappe.db.get_all(
			"Lab Invoice",
			filters={
				"referred_by": self.doctor,
				"invoice_date": ["between", [self.period_from, self.period_to]],
				"docstatus": 1,
				"commission_settled": 0,
				"branch": self.branch or ["!=", ""]
			},
			fields=["name", "patient_name", "invoice_date", "grand_total", "commission_amount"]
		)
		self.items = []
		for inv in invoices:
			self.append("items", {
				"lab_invoice": inv.name,
				"commission_amount": inv.commission_amount or 0
			})
		self._compute_totals()
