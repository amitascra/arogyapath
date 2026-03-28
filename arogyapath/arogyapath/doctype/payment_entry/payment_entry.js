// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Entry', {
	refresh: function(frm) {
		// Set filters based on payment type
		frm.trigger('set_party_filters');
		frm.trigger('set_reference_filters');
		
		// Calculate amounts on refresh
		frm.trigger('calculate_amounts');
	},
	
	payment_type: function(frm) {
		frm.trigger('set_party_filters');
		frm.trigger('set_reference_filters');
	},
	
	party_type: function(frm) {
		// Clear party when party type changes
		frm.set_value('party', '');
		frm.set_value('party_name', '');
	},
	
	party: function(frm) {
		if (frm.doc.party && frm.doc.party_type) {
			// Fetch party name
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: frm.doc.party_type,
					filters: {name: frm.doc.party},
					fieldname: get_party_name_field(frm.doc.party_type)
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('party_name', r.message[get_party_name_field(frm.doc.party_type)]);
					}
				}
			});
		}
	},
	
	paid_amount: function(frm) {
		// Auto-set received amount if not set
		if (!frm.doc.received_amount) {
			frm.set_value('received_amount', frm.doc.paid_amount);
		}
		frm.trigger('calculate_amounts');
	},
	
	received_amount: function(frm) {
		frm.trigger('calculate_amounts');
	},
	
	calculate_amounts: function(frm) {
		// Calculate total allocated amount
		let total_allocated = 0;
		if (frm.doc.references) {
			frm.doc.references.forEach(function(row) {
				total_allocated += flt(row.allocated_amount);
			});
		}
		frm.set_value('total_allocated_amount', total_allocated);
		
		// Calculate total deductions
		let total_deductions = 0;
		if (frm.doc.deductions) {
			frm.doc.deductions.forEach(function(row) {
				total_deductions += flt(row.amount);
			});
		}
		
		// Calculate unallocated amount
		let unallocated = flt(frm.doc.paid_amount) - total_allocated - total_deductions;
		frm.set_value('unallocated_amount', unallocated);
		
		// Calculate difference amount
		let difference = flt(frm.doc.received_amount) - flt(frm.doc.paid_amount);
		frm.set_value('difference_amount', difference);
		
		// Show warning if difference is not zero
		if (Math.abs(difference) > 0.01) {
			frm.dashboard.set_headline_alert(
				'Difference amount must be zero before submitting',
				'orange'
			);
		} else {
			frm.dashboard.clear_headline();
		}
	},
	
	set_party_filters: function(frm) {
		// Set filters for party based on payment type
		if (frm.doc.payment_type === 'Receive') {
			frm.set_df_property('party_type', 'options', '\nPatient\nCorporate Account');
		} else if (frm.doc.payment_type === 'Pay') {
			frm.set_df_property('party_type', 'options', '\nSupplier\nDoctor\nEmployee\nPatient');
		}
	},
	
	set_reference_filters: function(frm) {
		// Set filters for reference documents based on payment type
		if (frm.doc.payment_type === 'Receive') {
			frm.fields_dict.references.grid.update_docfield_property(
				'reference_doctype',
				'options',
				'Lab Invoice\nSales Return'
			);
		} else if (frm.doc.payment_type === 'Pay') {
			frm.fields_dict.references.grid.update_docfield_property(
				'reference_doctype',
				'options',
				'Purchase Invoice\nDoctor Commission Log\nPurchase Return'
			);
		}
	}
});

// Child table: Payment Entry Reference
frappe.ui.form.on('Payment Entry Reference', {
	reference_name: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		if (row.reference_doctype && row.reference_name) {
			// Fetch outstanding amount
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: row.reference_doctype,
					name: row.reference_name
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'total_amount', r.message.grand_total || 0);
						frappe.model.set_value(cdt, cdn, 'outstanding_amount', r.message.outstanding_amount || r.message.grand_total || 0);
						frappe.model.set_value(cdt, cdn, 'allocated_amount', r.message.outstanding_amount || r.message.grand_total || 0);
					}
				}
			});
		}
	},
	
	allocated_amount: function(frm, cdt, cdn) {
		frm.trigger('calculate_amounts');
	},
	
	references_remove: function(frm) {
		frm.trigger('calculate_amounts');
	}
});

// Child table: Payment Entry Deduction
frappe.ui.form.on('Payment Entry Deduction', {
	amount: function(frm) {
		frm.trigger('calculate_amounts');
	},
	
	deductions_remove: function(frm) {
		frm.trigger('calculate_amounts');
	}
});

// Helper function to get party name field
function get_party_name_field(party_type) {
	const name_fields = {
		'Patient': 'full_name',
		'Supplier': 'supplier_name',
		'Doctor': 'doctor_name',
		'Employee': 'employee_name',
		'Corporate Account': 'account_name'
	};
	return name_fields[party_type] || 'name';
}
