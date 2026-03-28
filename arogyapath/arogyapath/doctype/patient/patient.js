// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient', {
	refresh: function(frm) {
		// Add custom buttons or logic here
	},
	
	date_of_birth: function(frm) {
		// Auto-calculate age when DOB changes
		if (frm.doc.date_of_birth) {
			let dob = frappe.datetime.str_to_obj(frm.doc.date_of_birth);
			let today = new Date();
			let age = Math.floor((today - dob) / (365.25 * 24 * 60 * 60 * 1000));
			frm.set_value('age', age);
		}
	}
});
