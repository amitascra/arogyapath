// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('QC Result', {
	refresh: function(frm) {
		if (frm.doc.overall_status === 'Reject') {
			frm.dashboard.add_indicator(__('QC Failed - Results on Hold'), 'red');
		} else if (frm.doc.overall_status === 'Warning') {
			frm.dashboard.add_indicator(__('QC Warning - Review Required'), 'orange');
		} else if (frm.doc.overall_status === 'Pass') {
			frm.dashboard.add_indicator(__('QC Passed'), 'green');
		}
	},

	qc_material: function(frm) {
		if (frm.doc.qc_material) {
			frappe.db.get_doc('QC Material', frm.doc.qc_material).then(function(mat) {
				frm.clear_table('items');
				let row = frm.add_child('items');
				row.parameter = mat.material_name;
				row.target_mean = mat.target_mean;
				row.target_sd = mat.target_sd;
				frm.refresh_field('items');
			});
		}
	}
});
