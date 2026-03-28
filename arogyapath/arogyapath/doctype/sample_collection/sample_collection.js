// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sample Collection', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			if (!frm.doc.barcode_printed) {
				frm.add_custom_button(__('Print Barcode Label'), function() {
					frappe.set_route('print', frm.doc.doctype, frm.doc.name, {
						format: 'Barcode Label'
					});
					frm.set_value('barcode_printed', 1);
					frm.save();
				}, __('Actions'));
			}

			frm.add_custom_button(__('Mark as Received'), function() {
				frm.set_value('status', 'Received');
				frm.set_value('received_by', frappe.session.user);
				frm.set_value('received_at', frappe.datetime.now_datetime());
				frm.save();
			}, __('Actions'));
		}
	},

	patient_visit: function(frm) {
		if (frm.doc.patient_visit) {
			frappe.db.get_value('Patient Visit', frm.doc.patient_visit, ['patient', 'branch'], function(r) {
				if (r) {
					frm.set_value('patient', r.patient);
					frm.set_value('branch', r.branch);
				}
			});
		}
	}
});
