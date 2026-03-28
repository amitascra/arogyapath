// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Doctor Commission Log', {
	refresh: function(frm) {
		if (frm.doc.status === 'Draft') {
			frm.add_custom_button(__('Fetch Unsettled Invoices'), function() {
				if (!frm.doc.doctor || !frm.doc.period_from || !frm.doc.period_to) {
					frappe.msgprint(__('Please set Doctor, Period From and Period To first'));
					return;
				}
				frappe.call({
					method: 'fetch_unsettled_invoices',
					doc: frm.doc,
					callback: function(r) {
						frm.refresh_field('items');
						frm.refresh_field('total_invoiced');
						frm.refresh_field('total_commission');
						frm.refresh_field('tds_amount');
						frm.refresh_field('net_payable');
					}
				});
			});
		}
	}
});
