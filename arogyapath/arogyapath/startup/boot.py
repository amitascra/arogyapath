# Copyright (c) 2026, Ascratech and contributors
# Boot session handler for ArogyaPath

import frappe
from frappe import _


def boot_session(bootinfo):
    """
    Boot session - add custom data to bootinfo
    Called when user logs in
    """
    if frappe.session.user == "Guest":
        return
    
    # Add page info for tree views
    bootinfo.page_info.update({
        "Chart of Accounts": {
            "title": _("Chart of Accounts"),
            "route": "Tree/Account"
        }
    })
    
    # Add system defaults
    bootinfo.sysdefaults.default_currency = "INR"
    
    # Get user's default branch
    employee = frappe.db.get_value("Employee", {"user": frappe.session.user}, "name")
    if employee:
        bootinfo.sysdefaults.default_branch = frappe.db.get_value("Employee", employee, "branch")
        bootinfo["user"]["employee"] = employee
    
    # Add lab-specific data
    bootinfo.pending_results_count = get_pending_results_count()
    bootinfo.today_orders_count = get_today_orders_count()
    bootinfo.outstanding_amount = get_outstanding_amount()
    
    # Check setup completion
    bootinfo.setup_complete = check_setup_complete()


def get_pending_results_count():
    """Get count of pending lab results"""
    try:
        return frappe.db.count("Lab Result", {"status": ["in", ["Draft", "In Progress"]]})
    except Exception:
        return 0


def get_today_orders_count():
    """Get count of today's lab orders"""
    try:
        from frappe.utils import today
        return frappe.db.count("Lab Order", {"posting_date": today()})
    except Exception:
        return 0


def get_outstanding_amount():
    """Get total outstanding amount"""
    try:
        result = frappe.db.sql("""
            SELECT SUM(outstanding_amount)
            FROM `tabLab Invoice`
            WHERE docstatus = 1 AND outstanding_amount > 0
        """)
        return result[0][0] if result and result[0][0] else 0
    except Exception:
        return 0


def check_setup_complete():
    """Check if initial setup is complete"""
    try:
        # Check if at least one branch exists
        if not frappe.db.exists("Lab Branch"):
            return False
        
        # Check if at least one test exists
        if not frappe.db.exists("Lab Test Master"):
            return False
        
        return True
    except Exception:
        return False
