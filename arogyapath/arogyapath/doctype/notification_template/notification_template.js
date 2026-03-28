// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Notification Template', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Preview'), function() {
				frappe.msgprint({
					title: frm.doc.subject || frm.doc.template_name,
					message: frm.doc.message_body
						.replace('{{ patient_name }}', '<b>John Doe</b>')
						.replace('{{ report_url }}', '<a href="#">https://pathlab.localhost/report/abc123</a>')
						.replace('{{ test_name }}', 'CBC')
						.replace('{{ lab_name }}', 'ArogyaPath Labs'),
					indicator: 'blue'
				});
			});
		}
	},

	channel: function(frm) {
		frm.toggle_reqd('subject', frm.doc.channel === 'Email');
	}
});
