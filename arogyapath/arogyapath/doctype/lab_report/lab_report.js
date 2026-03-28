// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Report', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Send via WhatsApp'), function() {
				frappe.call({
					method: 'arogyapath.arogyapath.doctype.lab_report.lab_report.send_whatsapp_report',
					args: { lab_report: frm.doc.name },
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint(__('Report sent via WhatsApp'));
							frm.reload_doc();
						}
					}
				});
			}, __('Deliver'));

			frm.add_custom_button(__('Send via Email'), function() {
				frappe.call({
					method: 'arogyapath.arogyapath.doctype.lab_report.lab_report.send_email_report',
					args: { lab_report: frm.doc.name },
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint(__('Report sent via Email'));
							frm.reload_doc();
						}
					}
				});
			}, __('Deliver'));

			frm.add_custom_button(__('Print Report'), function() {
				frappe.set_route('print', frm.doc.doctype, frm.doc.name);
			}, __('Deliver'));

			if (frm.doc.report_url_token) {
				frm.add_custom_button(__('View Patient Portal'), function() {
					let settings_call = frappe.call({
						method: 'frappe.client.get_single_value',
						args: { doctype: 'Lab Settings', field: 'report_portal_url' },
						callback: function(r) {
							let base = r.message || window.location.origin;
							window.open(base + '/report/' + frm.doc.report_url_token, '_blank');
						}
					});
				});
			}
		}
	}
});
