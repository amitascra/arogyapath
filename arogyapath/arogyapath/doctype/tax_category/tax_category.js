// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Category', {
	refresh: function(frm) {
		// Set indicator based on disabled status
		if (frm.doc.disabled) {
			frm.set_indicator(__('Disabled'), 'red');
		} else {
			frm.set_indicator(__('Active'), 'green');
		}
	}
});
