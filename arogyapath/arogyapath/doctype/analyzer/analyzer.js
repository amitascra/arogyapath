// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Analyzer', {
	refresh: function(frm) {
		if (frm.doc.amc_expiry_date) {
			let today = frappe.datetime.get_today();
			let days = frappe.datetime.get_diff(frm.doc.amc_expiry_date, today);
			if (days < 0) {
				frm.dashboard.add_indicator(__('AMC Expired'), 'red');
			} else if (days <= 30) {
				frm.dashboard.add_indicator(__('AMC Expiring in {0} days', [days]), 'orange');
			}
		}
	}
});
