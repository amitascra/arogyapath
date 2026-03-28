// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Result', {
	refresh: function(frm) {
		// Approve buttons based on current status
		if (!frm.is_new()) {
			if (frm.doc.validation_status === 'Draft' && frappe.user.has_role('Lab Technician')) {
				frm.add_custom_button(__('Tech Approve'), function() {
					frm.set_value('validation_status', 'Tech Approved');
					frm.save();
				}, __('Actions'));
			}

			if (frm.doc.validation_status === 'Tech Approved' && frappe.user.has_role('Lab Pathologist')) {
				frm.add_custom_button(__('Pathologist Approve'), function() {
					frm.set_value('validation_status', 'Pathologist Approved');
					frm.save();
				}, __('Actions'));
			}

			// Load reference ranges button
			frm.add_custom_button(__('Load Reference Ranges'), function() {
				frappe.call({
					method: 'arogyapath.arogyapath.doctype.lab_result.lab_result.load_reference_ranges',
					args: { lab_result: frm.doc.name },
					callback: function(r) {
						frm.reload_doc();
					}
				});
			});

			// Highlight critical values in the result items table
			frm.doc.items && frm.doc.items.forEach(function(item) {
				if (item.flag === 'Critical Low' || item.flag === 'Critical High') {
					frm.get_field('items').grid.grid_rows.forEach(function(row) {
						if (row.doc.name === item.name) {
							row.row.addClass('bg-danger-subtle');
						}
					});
				}
			});
		}
	},

	test: function(frm) {
		// Auto-populate result items from test parameters
		if (frm.doc.test && frm.is_new()) {
			frappe.db.get_doc('Lab Test Master', frm.doc.test).then(function(test) {
				frm.clear_table('items');
				test.parameters.forEach(function(param) {
					let row = frm.add_child('items');
					row.parameter_name = param.parameter_name;
					row.parameter_code = param.parameter_code;
					row.unit = param.unit;
				});
				frm.refresh_field('items');
			});
		}
	}
});

frappe.ui.form.on('Lab Result Item', {
	result_value: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Try to parse numeric value
		let num = parseFloat(row.result_value);
		if (!isNaN(num)) {
			frappe.model.set_value(cdt, cdn, 'result_numeric', num);
		}
	}
});
