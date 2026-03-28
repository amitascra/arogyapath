// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Test Master', {
	refresh: function(frm) {
		// Add custom buttons or logic here
	},

	department: function(frm) {
		if (frm.doc.department && !frm.doc.tat_hours) {
			frappe.db.get_value('Lab Department', frm.doc.department, 'turnaround_hours', function(r) {
				if (r && r.turnaround_hours) {
					frm.set_value('tat_hours', r.turnaround_hours);
				}
			});
		}
	},

	test_code: function(frm) {
		if (frm.doc.test_code) {
			frm.set_value('test_code', frm.doc.test_code.toUpperCase());
		}
	}
});
