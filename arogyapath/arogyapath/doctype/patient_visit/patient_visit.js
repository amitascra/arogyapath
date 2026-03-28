// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Visit', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Lab Order'), function() {
				frappe.new_doc('Lab Order', {
					patient_visit: frm.doc.name,
					patient: frm.doc.patient,
					branch: frm.doc.branch,
					referred_by: frm.doc.referred_by
				});
			});
		}
	}
});
