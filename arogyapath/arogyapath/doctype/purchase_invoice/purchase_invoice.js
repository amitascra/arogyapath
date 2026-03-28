// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.js

frappe.ui.form.on('Purchase Invoice', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
			frm.add_custom_button(__('Make Payment'), function() {
				frappe.model.open_mapped_doc({
					method: 'arogyapath.arogyapath.doctype.purchase_invoice.purchase_invoice.make_payment_entry',
					frm: frm
				});
			});
		}
		
		// Calculate totals on refresh
		frm.trigger('calculate_totals');
	},
	
	supplier: function(frm) {
		if (frm.doc.supplier) {
			// Fetch supplier details
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Supplier',
					name: frm.doc.supplier
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('supplier_name', r.message.supplier_name);
						frm.set_value('payment_terms', r.message.payment_terms);
						frm.set_value('supplier_gstin', r.message.gstin);
						
						// Set TDS details
						if (r.message.tax_withholding_category) {
							frm.set_value('tds_applicable', 1);
							frm.set_value('tds_category', r.message.tax_withholding_category);
						}
						
						// Calculate due date
						if (r.message.credit_days && frm.doc.posting_date) {
							let due_date = frappe.datetime.add_days(frm.doc.posting_date, r.message.credit_days);
							frm.set_value('due_date', due_date);
						}
					}
				}
			});
		}
	},
	
	posting_date: function(frm) {
		// Recalculate due date if credit days available
		if (frm.doc.supplier) {
			frappe.db.get_value('Supplier', frm.doc.supplier, 'credit_days', function(r) {
				if (r && r.credit_days) {
					let due_date = frappe.datetime.add_days(frm.doc.posting_date, r.credit_days);
					frm.set_value('due_date', due_date);
				}
			});
		}
	},
	
	calculate_totals: function(frm) {
		let total_qty = 0;
		let base_total = 0;
		let total_cgst = 0;
		let total_sgst = 0;
		let total_igst = 0;
		
		// Calculate from items
		if (frm.doc.items) {
			frm.doc.items.forEach(function(item) {
				total_qty += flt(item.qty);
				base_total += flt(item.amount);
				total_cgst += flt(item.cgst_amount);
				total_sgst += flt(item.sgst_amount);
				total_igst += flt(item.igst_amount);
			});
		}
		
		// Set totals
		frm.set_value('total_qty', total_qty);
		frm.set_value('base_total', base_total);
		frm.set_value('total_cgst', total_cgst);
		frm.set_value('total_sgst', total_sgst);
		frm.set_value('total_igst', total_igst);
		
		let total_tax = total_cgst + total_sgst + total_igst;
		frm.set_value('total_tax', total_tax);
		
		let grand_total = base_total + total_tax;
		frm.set_value('grand_total', grand_total);
		
		// Calculate TDS
		if (frm.doc.tds_applicable && frm.doc.tds_rate) {
			let tds_amount = flt(base_total * frm.doc.tds_rate / 100, 2);
			frm.set_value('tds_amount', tds_amount);
		}
		
		// Set outstanding
		if (frm.doc.docstatus === 0) {
			frm.set_value('outstanding_amount', grand_total);
		}
	}
});

// Child table: Purchase Invoice Item
frappe.ui.form.on('Purchase Invoice Item', {
	item: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		if (row.item) {
			// Fetch item details
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Item',
					name: row.item
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
						frappe.model.set_value(cdt, cdn, 'description', r.message.description);
						frappe.model.set_value(cdt, cdn, 'uom', r.message.stock_uom);
						frappe.model.set_value(cdt, cdn, 'gst_hsn_code', r.message.gst_hsn_code);
						
						// Set rate from last purchase rate or standard rate
						let rate = r.message.last_purchase_rate || r.message.standard_rate || 0;
						frappe.model.set_value(cdt, cdn, 'rate', rate);
					}
				}
			});
		}
	},
	
	qty: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	cgst_rate: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	sgst_rate: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	igst_rate: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	items_remove: function(frm) {
		frm.trigger('calculate_totals');
	}
});

function calculate_item_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	
	// Calculate base amount
	row.amount = flt(row.qty) * flt(row.rate);
	
	// Set default tax rates if not set
	if (!row.cgst_rate && !row.sgst_rate && !row.igst_rate) {
		if (frm.doc.is_interstate) {
			row.igst_rate = 18.0;
			row.cgst_rate = 0;
			row.sgst_rate = 0;
		} else {
			row.cgst_rate = 9.0;
			row.sgst_rate = 9.0;
			row.igst_rate = 0;
		}
	}
	
	// Calculate tax amounts
	row.cgst_amount = flt(row.amount * row.cgst_rate / 100, 2);
	row.sgst_amount = flt(row.amount * row.sgst_rate / 100, 2);
	row.igst_amount = flt(row.amount * row.igst_rate / 100, 2);
	
	// Calculate total amount
	row.total_amount = flt(row.amount) + flt(row.cgst_amount) + flt(row.sgst_amount) + flt(row.igst_amount);
	
	// Refresh the row
	frm.refresh_field('items');
	
	// Recalculate totals
	frm.trigger('calculate_totals');
}
