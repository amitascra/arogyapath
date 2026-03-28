# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet


class PathologyLab(NestedSet):
    """Top-level organization representing a Pathology Laboratory"""
    
    nsm_parent_field = 'parent_lab'
    
    def validate(self):
        """Validate Pathology Lab"""
        self.validate_abbr()
        self.validate_parent_lab()
    
    def validate_abbr(self):
        """Validate abbreviation is unique and alphanumeric"""
        if not self.abbr:
            frappe.throw(_("Abbreviation is required"))
        
        # Check if abbr is alphanumeric
        if not self.abbr.replace("_", "").replace("-", "").isalnum():
            frappe.throw(_("Abbreviation must be alphanumeric"))
        
        # Check uniqueness
        if self.is_new():
            existing = frappe.db.get_value("Pathology Lab", 
                {"abbr": self.abbr, "name": ["!=", self.name]}, "name")
            if existing:
                frappe.throw(_("Abbreviation {0} already used in {1}").format(
                    frappe.bold(self.abbr), frappe.bold(existing)))
    
    def validate_parent_lab(self):
        """Validate parent lab relationship"""
        if self.parent_lab:
            if self.parent_lab == self.name:
                frappe.throw(_("Lab cannot be its own parent"))
            
            # Check if parent is a group
            parent_is_group = frappe.db.get_value("Pathology Lab", 
                self.parent_lab, "is_group")
            if not parent_is_group:
                frappe.throw(_("Parent Lab {0} must be a group").format(
                    frappe.bold(self.parent_lab)))
    
    def on_update(self):
        """Update nested set after save"""
        super(PathologyLab, self).on_update()
        
        # Update default lab in Lab Settings if this is the first lab
        if not frappe.db.exists("Lab Settings", "Lab Settings"):
            return
        
        lab_settings = frappe.get_doc("Lab Settings", "Lab Settings")
        if not lab_settings.default_lab:
            lab_settings.default_lab = self.name
            lab_settings.save(ignore_permissions=True)
    
    def on_trash(self):
        """Prevent deletion if lab has branches"""
        # Check if lab has branches
        branches = frappe.get_all("Lab Branch", 
            filters={"pathology_lab": self.name}, 
            limit=1)
        
        if branches:
            frappe.throw(_("Cannot delete Pathology Lab {0} as it has branches. Please delete all branches first.").format(
                frappe.bold(self.name)))
        
        super(PathologyLab, self).on_trash()
    
    def get_branches(self):
        """Get all branches under this lab"""
        return frappe.get_all("Lab Branch",
            filters={"pathology_lab": self.name},
            fields=["name", "branch_name", "branch_code", "is_active"],
            order_by="branch_name")
    
    def get_active_branches_count(self):
        """Get count of active branches"""
        return frappe.db.count("Lab Branch", 
            {"pathology_lab": self.name, "is_active": 1})


@frappe.whitelist()
def get_lab_tree():
    """Get pathology lab tree structure"""
    labs = frappe.get_all("Pathology Lab",
        fields=["name", "lab_name", "parent_lab", "is_group", "lft", "rgt"],
        order_by="lft")
    
    return labs
