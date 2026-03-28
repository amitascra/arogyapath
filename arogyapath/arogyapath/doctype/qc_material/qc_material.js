// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('QC Material', {
	refresh: function(frm) {
		// Add custom buttons or logic here
	},

	target_mean: function(frm) {
		if (frm.doc.target_mean && frm.doc.target_sd) {
			let cv = (frm.doc.target_sd / frm.doc.target_mean) * 100;
			frm.set_value('cv_percent', Math.round(cv * 100) / 100);
		}
	},

	target_sd: function(frm) {
		frm.trigger('target_mean');
	}
});
