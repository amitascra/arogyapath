// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.js

frappe.ui.form.on('Sales Return', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
			frm.add_custom_button(__('Make Refund Payment'), function() {
				frappe.model.open_mapped_doc({
					method: 'arogyapath.arogyapath.doctype.sales_return.sales_return.make_refund_payment',
					frm: frm
				});
			});
		}
		
		// Calculate totals on refresh
		frm.trigger('calculate_totals');
	},
	
	return_against: function(frm) {
		if (frm.doc.return_against) {
			// Fetch invoice details and populate items
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Lab Invoice',
					name: frm.doc.return_against
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('patient', r.message.patient);
						frm.set_value('patient_name', r.message.patient_name);
						frm.set_value('branch', r.message.branch);
						
						// Clear existing items
						frm.clear_table('items');
						
						// Add invoice items
						if (r.message.items) {
							r.message.items.forEach(function(item) {
								let row = frm.add_child('items');
								row.lab_invoice_item = item.name;
								row.test = item.test;
								row.test_name = item.test_name;
								row.qty = item.qty;
								row.rate = item.rate;
								row.amount = item.amount;
							});
						}
						
						frm.refresh_field('items');
						frm.trigger('calculate_totals');
					}
				}
			});
		}
	},
	
	calculate_totals: function(frm) {
		let total_qty = 0;
		let base_total = 0;
		
		// Calculate from items
		if (frm.doc.items) {
			frm.doc.items.forEach(function(item) {
				total_qty += flt(item.qty);
				base_total += flt(item.amount);
			});
		}
		
		// Set totals
		frm.set_value('total_qty', total_qty);
		frm.set_value('base_total', base_total);
		
		// Calculate taxes (proportional to original invoice)
		if (frm.doc.return_against && base_total > 0) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Lab Invoice',
					name: frm.doc.return_against
				},
				callback: function(r) {
					if (r.message && r.message.base_total > 0) {
						let invoice = r.message;
						let tax_ratio = (invoice.total_cgst + invoice.total_sgst + invoice.total_igst) / invoice.base_total;
						
						let total_cgst = flt(base_total * (invoice.total_cgst / invoice.base_total), 2);
						let total_sgst = flt(base_total * (invoice.total_sgst / invoice.base_total), 2);
						let total_igst = flt(base_total * (invoice.total_igst / invoice.base_total), 2);
						
						frm.set_value('total_cgst', total_cgst);
						frm.set_value('total_sgst', total_sgst);
						frm.set_value('total_igst', total_igst);
						
						let total_tax = total_cgst + total_sgst + total_igst;
						frm.set_value('total_tax', total_tax);
						
						let grand_total = base_total + total_tax;
						frm.set_value('grand_total', grand_total);
						
						// Set outstanding
						if (frm.doc.docstatus === 0) {
							frm.set_value('outstanding_amount', grand_total);
						}
					}
				}
			});
		}
	}
});

// Child table: Sales Return Item
frappe.ui.form.on('Sales Return Item', {
	qty: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	rate: function(frm, cdt, cdn) {
		calculate_item_amount(frm, cdt, cdn);
	},
	
	items_remove: function(frm) {
		frm.trigger('calculate_totals');
	}
});

function calculate_item_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	row.amount = flt(row.qty) * flt(row.rate);
	frm.refresh_field('items');
	frm.trigger('calculate_totals');
}
