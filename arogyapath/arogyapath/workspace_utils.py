# Copyright (c) 2026, Ascratech and contributors
# Workspace utility functions for KPI number cards

import frappe
from frappe import _
from frappe.utils import today, flt, nowdate, add_days


# ==================== Home Workspace KPIs ====================

@frappe.whitelist()
def get_todays_orders_count():
    """Get count of lab orders created today"""
    return frappe.db.count("Lab Order", {"posting_date": today()})


@frappe.whitelist()
def get_pending_results_count():
    """Get count of pending lab results"""
    return frappe.db.count("Lab Result", {"status": ["in", ["Draft", "In Progress"]]})


@frappe.whitelist()
def get_todays_revenue():
    """Get total revenue from lab invoices today"""
    result = frappe.db.sql("""
        SELECT SUM(grand_total) as revenue
        FROM `tabLab Invoice`
        WHERE posting_date = %s AND docstatus = 1
    """, (today(),))
    return flt(result[0][0]) if result and result[0][0] else 0


@frappe.whitelist()
def get_outstanding_amount():
    """Get total outstanding amount from unpaid invoices"""
    result = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as outstanding
        FROM `tabLab Invoice`
        WHERE docstatus = 1 AND outstanding_amount > 0
    """)
    return flt(result[0][0]) if result and result[0][0] else 0


# ==================== Patient Management KPIs ====================

@frappe.whitelist()
def get_total_patients():
    """Get total number of patients"""
    return frappe.db.count("Patient")


@frappe.whitelist()
def get_new_patients_today():
    """Get count of patients registered today"""
    return frappe.db.count("Patient", {"creation": [">=", today()]})


@frappe.whitelist()
def get_active_visits():
    """Get count of active patient visits"""
    return frappe.db.count("Patient Visit", {"status": ["in", ["Open", "In Progress"]]})


@frappe.whitelist()
def get_samples_collected_today():
    """Get count of samples collected today"""
    return frappe.db.count("Sample Collection", {"collection_date": today()})


# ==================== Lab Operations KPIs ====================

@frappe.whitelist()
def get_completed_results_today():
    """Get count of lab results completed today"""
    return frappe.db.count("Lab Result", {
        "status": "Released",
        "modified": [">=", today()]
    })


@frappe.whitelist()
def get_critical_results():
    """Get count of critical lab results"""
    return frappe.db.sql("""
        SELECT COUNT(DISTINCT lr.name)
        FROM `tabLab Result` lr
        INNER JOIN `tabLab Result Item` lri ON lri.parent = lr.name
        WHERE lri.is_critical = 1 AND lr.status != 'Cancelled'
    """)[0][0] or 0


@frappe.whitelist()
def get_reports_generated_today():
    """Get count of lab reports generated today"""
    return frappe.db.count("Lab Report", {"creation": [">=", today()]})


# ==================== Billing & Finance KPIs ====================

@frappe.whitelist()
def get_payments_received_today():
    """Get total payments received today"""
    result = frappe.db.sql("""
        SELECT SUM(paid_amount) as total
        FROM `tabPayment Entry`
        WHERE posting_date = %s AND docstatus = 1
    """, (today(),))
    return flt(result[0][0]) if result and result[0][0] else 0


@frappe.whitelist()
def get_invoices_generated_today():
    """Get count of invoices generated today"""
    return frappe.db.count("Lab Invoice", {"posting_date": today()})


# ==================== Inventory & Purchase KPIs ====================

@frappe.whitelist()
def get_low_stock_items():
    """Get count of reagents with low stock"""
    return frappe.db.sql("""
        SELECT COUNT(DISTINCT r.name)
        FROM `tabReagent` r
        WHERE r.current_stock <= r.reorder_level
        AND r.current_stock > 0
    """)[0][0] or 0


@frappe.whitelist()
def get_expiring_reagents():
    """Get count of reagents expiring in next 30 days"""
    expiry_date = add_days(nowdate(), 30)
    return frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabReagent Lot`
        WHERE expiry_date <= %s
        AND expiry_date >= %s
        AND current_quantity > 0
    """, (expiry_date, nowdate()))[0][0] or 0


@frappe.whitelist()
def get_stock_value():
    """Get total stock value"""
    result = frappe.db.sql("""
        SELECT SUM(stock_value)
        FROM `tabStock Ledger Entry`
        WHERE docstatus < 2
    """)
    return flt(result[0][0]) if result and result[0][0] else 0


@frappe.whitelist()
def get_purchase_orders_count():
    """Get count of purchase invoices this month"""
    return frappe.db.count("Purchase Invoice", {
        "posting_date": [">=", frappe.utils.get_first_day(today())]
    })


# ==================== Quality Control KPIs ====================

@frappe.whitelist()
def get_qc_tests_today():
    """Get count of QC tests performed today"""
    return frappe.db.count("QC Result", {"test_date": today()})


@frappe.whitelist()
def get_out_of_control_qc():
    """Get count of out-of-control QC results"""
    return frappe.db.count("QC Result", {
        "qc_status": "Out of Control",
        "test_date": [">=", add_days(today(), -7)]
    })


@frappe.whitelist()
def get_calibrations_due():
    """Get count of calibrations due in next 7 days"""
    due_date = add_days(nowdate(), 7)
    return frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabAnalyzer`
        WHERE next_calibration_date <= %s
        AND next_calibration_date >= %s
        AND disabled = 0
    """, (due_date, nowdate()))[0][0] or 0


@frappe.whitelist()
def get_active_analyzers():
    """Get count of active analyzers"""
    return frappe.db.count("Analyzer", {"disabled": 0})
