// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pathology Lab', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Branches'), function() {
                frappe.set_route('List', 'Lab Branch', {
                    'pathology_lab': frm.doc.name
                });
            });
            
            // Show branch count
            if (frm.doc.__onload && frm.doc.__onload.branch_count) {
                frm.dashboard.add_indicator(__('Branches: {0}', [frm.doc.__onload.branch_count]), 
                    frm.doc.__onload.branch_count > 0 ? 'blue' : 'gray');
            }
        }
        
        // Set mandatory fields
        frm.set_df_property('abbr', 'read_only', !frm.is_new());
    },
    
    lab_name: function(frm) {
        // Auto-generate abbreviation from lab name
        if (frm.is_new() && frm.doc.lab_name && !frm.doc.abbr) {
            let abbr = frm.doc.lab_name
                .split(' ')
                .map(word => word.charAt(0).toUpperCase())
                .join('')
                .substring(0, 5);
            frm.set_value('abbr', abbr);
        }
    },
    
    is_group: function(frm) {
        // Show/hide parent lab field
        frm.toggle_reqd('parent_lab', frm.doc.is_group);
    }
});
