// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Order', {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Create Lab Result'), function() {
				frappe.call({
					method: 'arogyapath.arogyapath.controllers.lab_order.create_results_for_order',
					args: { lab_order: frm.doc.name },
					callback: function(r) {
						if (!r.exc) {
							frappe.msgprint(__('Lab Results created successfully'));
							frm.reload_doc();
						}
					}
				});
			});

			frm.add_custom_button(__('Create Invoice'), function() {
				frappe.new_doc('Lab Invoice', {
					lab_order: frm.doc.name,
					patient: frm.doc.patient,
					branch: frm.doc.branch,
					referred_by: frm.doc.referred_by
				});
			});
		}
	},

	patient_visit: function(frm) {
		if (frm.doc.patient_visit) {
			frappe.db.get_value('Patient Visit',
				frm.doc.patient_visit,
				['patient', 'branch', 'referred_by'],
				function(r) {
					if (r) {
						frm.set_value('patient', r.patient);
						frm.set_value('branch', r.branch);
						frm.set_value('referred_by', r.referred_by);
					}
				}
			);
		}
	}
});

frappe.ui.form.on('Lab Order Item', {
	test: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.test) {
			frappe.db.get_value('Lab Test Master', row.test,
				['test_name', 'cost', 'department', 'sample_type', 'is_outsourced'],
				function(r) {
					if (r) {
						frappe.model.set_value(cdt, cdn, 'test_name', r.test_name);
						frappe.model.set_value(cdt, cdn, 'rate', r.cost);
						frappe.model.set_value(cdt, cdn, 'department', r.department);
						frappe.model.set_value(cdt, cdn, 'sample_type', r.sample_type);
						frappe.model.set_value(cdt, cdn, 'is_outsourced', r.is_outsourced);
					}
				}
			);
		}
	}
});
