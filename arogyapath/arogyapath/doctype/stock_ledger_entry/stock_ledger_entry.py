# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now


class StockLedgerEntry(Document):
	def validate(self):
		"""Validate stock ledger entry"""
		self.calculate_stock_value()
		self.update_qty_after_transaction()
	
	def calculate_stock_value(self):
		"""Calculate stock value and difference"""
		if flt(self.actual_qty) > 0:
			# Incoming - use incoming rate
			self.stock_value_difference = flt(self.actual_qty) * flt(self.incoming_rate)
		else:
			# Outgoing - use outgoing rate
			self.stock_value_difference = flt(self.actual_qty) * flt(self.outgoing_rate)
		
		# Get previous stock value
		previous_sle = self.get_previous_sle()
		previous_stock_value = previous_sle.stock_value if previous_sle else 0
		
		self.stock_value = flt(previous_stock_value) + flt(self.stock_value_difference)
	
	def update_qty_after_transaction(self):
		"""Update quantity after transaction"""
		previous_sle = self.get_previous_sle()
		previous_qty = previous_sle.qty_after_transaction if previous_sle else 0
		
		self.qty_after_transaction = flt(previous_qty) + flt(self.actual_qty)
	
	def get_previous_sle(self):
		"""Get previous stock ledger entry for same item and warehouse"""
		previous = frappe.get_all(
			"Stock Ledger Entry",
			filters={
				"item": self.item,
				"warehouse": self.warehouse,
				"posting_date": ["<=", self.posting_date],
				"posting_time": ["<", self.posting_time or now()],
				"name": ["!=", self.name]
			},
			fields=["qty_after_transaction", "stock_value"],
			order_by="posting_date desc, posting_time desc",
			limit=1
		)
		
		return previous[0] if previous else None


def make_stock_entry(item, warehouse, actual_qty, voucher_type, voucher_no, 
					 posting_date=None, incoming_rate=0, outgoing_rate=0, 
					 batch_no=None, company=None, branch=None):
	"""
	Create a stock ledger entry
	
	Args:
		item: Item code
		warehouse: Warehouse/Branch
		actual_qty: Quantity (positive for receipt, negative for issue)
		voucher_type: Source document type
		voucher_no: Source document name
		posting_date: Posting date
		incoming_rate: Rate for incoming stock
		outgoing_rate: Rate for outgoing stock
		batch_no: Batch/Lot number
		company: Company
		branch: Lab Branch
	"""
	from frappe.utils import today, now
	
	if not posting_date:
		posting_date = today()
	
	sle = frappe.new_doc("Stock Ledger Entry")
	sle.posting_date = posting_date
	sle.posting_time = now()
	sle.item = item
	sle.warehouse = warehouse
	sle.actual_qty = actual_qty
	sle.voucher_type = voucher_type
	sle.voucher_no = voucher_no
	sle.incoming_rate = incoming_rate if actual_qty > 0 else 0
	sle.outgoing_rate = outgoing_rate if actual_qty < 0 else 0
	sle.batch_no = batch_no
	sle.company = company
	sle.branch = branch
	sle.insert(ignore_permissions=True)
	sle.submit()
	
	return sle
