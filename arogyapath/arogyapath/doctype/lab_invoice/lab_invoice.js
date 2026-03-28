// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Invoice', {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			if (frm.doc.outstanding_amount > 0) {
				frm.add_custom_button(__('Record Payment'), function() {
					frappe.prompt([
						{ label: __('Amount'), fieldname: 'amount', fieldtype: 'Currency', default: frm.doc.outstanding_amount, reqd: 1 },
						{ label: __('Payment Mode'), fieldname: 'mode', fieldtype: 'Select', options: 'Cash\nCard\nUPI', default: 'Cash' },
						{ label: __('Reference'), fieldname: 'ref', fieldtype: 'Data' }
					], function(values) {
						frappe.call({
							method: 'arogyapath.arogyapath.doctype.lab_invoice.lab_invoice.record_payment',
							args: {
								lab_invoice: frm.doc.name,
								amount: values.amount,
								payment_mode: values.mode,
								payment_reference: values.ref
							},
							callback: function(r) {
								if (!r.exc) {
									frm.reload_doc();
								}
							}
						});
					}, __('Record Payment'), __('Submit'));
				});
			}

			frm.add_custom_button(__('Send Invoice'), function() {
				frappe.set_route('print', frm.doc.doctype, frm.doc.name);
			});
		}

		// Auto-populate items from Lab Order
		if (frm.is_new() && frm.doc.lab_order) {
			frm.trigger('lab_order');
		}
	},

	lab_order: function(frm) {
		if (frm.doc.lab_order) {
			frappe.db.get_doc('Lab Order', frm.doc.lab_order).then(function(order) {
				frm.clear_table('items');
				order.tests.forEach(function(t) {
					if (t.status !== 'Cancelled') {
						let row = frm.add_child('items');
						row.test = t.test;
						row.test_name = t.test_name;
						row.mrp = t.rate;
						row.rate = t.rate;
						row.department = t.department;
					}
				});
				frm.refresh_field('items');
				frm.trigger('calculate_totals');
			});
		}
	},

	amount_paid: function(frm) {
		frm.trigger('calculate_totals');
	},

	discount_scheme: function(frm) {
		frm.save();
	},

	corporate_account: function(frm) {
		frm.save();
	},

	calculate_totals: function(frm) {
		let gross = 0, tax = 0;
		(frm.doc.items || []).forEach(function(item) {
			gross += flt(item.mrp);
			tax += flt(item.tax_amount);
		});
		frm.set_value('gross_amount', gross);
		let outstanding = flt(frm.doc.grand_total) - flt(frm.doc.amount_paid);
		frm.set_value('outstanding_amount', outstanding > 0 ? outstanding : 0);
	}
});

frappe.ui.form.on('Lab Invoice Item', {
	mrp: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'rate', flt(row.mrp) - flt(row.discount_amount));
	},
	discount_amount: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'rate', flt(row.mrp) - flt(row.discount_amount));
	}
});
