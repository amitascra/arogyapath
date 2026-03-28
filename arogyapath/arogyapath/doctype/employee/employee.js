// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('View User'), function() {
				frappe.set_route('Form', 'User', frm.doc.user);
			});
		}
		
		// Set filters for reporting manager
		frm.set_query('reporting_manager', function() {
			return {
				filters: {
					'name': ['!=', frm.doc.name],
					'is_active': 1
				}
			};
		});
		
		// Set filters for user - only show enabled users
		frm.set_query('user', function() {
			return {
				filters: {
					'enabled': 1,
					'user_type': 'System User'
				}
			};
		});
	},
	
	user: function(frm) {
		// Fetch company email when user is selected
		if (frm.doc.user) {
			frappe.db.get_value('User', frm.doc.user, 'email', function(r) {
				if (r && r.email) {
					frm.set_value('company_email', r.email);
				}
			});
			
			// Auto-fill employee name from user's full name if empty
			if (!frm.doc.employee_name) {
				frappe.db.get_value('User', frm.doc.user, 'full_name', function(r) {
					if (r && r.full_name) {
						frm.set_value('employee_name', r.full_name);
					}
				});
			}
		}
	},
	
	designation: function(frm) {
		// Show signature section if Pathologist is selected
		if (frm.doc.designation === 'Pathologist') {
			frm.set_df_property('section_break_signature', 'collapsible', 0);
			frappe.msgprint({
				title: __('Signature Required'),
				message: __('Please upload a signature image for pathologist reports'),
				indicator: 'blue'
			});
		}
	}
});

// Child table: Employee Role
frappe.ui.form.on('Employee Role', {
	role: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Warn if Lab Pathologist role is assigned without signature
		if (row.role === 'Lab Pathologist' && !frm.doc.signature_image) {
			frappe.msgprint({
				title: __('Signature Required'),
				message: __('Pathologists should have a signature image for reports'),
				indicator: 'orange'
			});
		}
	}
});
