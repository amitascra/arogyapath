import frappe
from frappe.utils import now_datetime, add_days, getdate, today, date_diff


def send_tat_alerts():
	"""Daily: notify technicians of Lab Orders approaching TAT deadline in next 2 hours"""
	try:
		from frappe.utils import add_to_date
		now = now_datetime()
		two_hours_later = add_to_date(now, hours=2)

		orders = frappe.db.get_all(
			"Lab Order",
			filters={
				"docstatus": 1,
				"status": ["in", ["Pending", "In Progress"]],
			},
			fields=["name", "patient", "branch", "tat_deadline", "owner"],
		)

		for order in orders:
			if not order.tat_deadline:
				continue
			deadline = frappe.utils.get_datetime(order.tat_deadline)
			if now <= deadline <= two_hours_later:
				frappe.publish_realtime(
					"tat_alert",
					{"message": f"TAT approaching for Lab Order {order.name}", "order": order.name},
					user=order.owner,
				)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: send_tat_alerts failed")


def check_critical_tat_breach():
	"""Hourly: flag Lab Orders that have breached TAT as Critical"""
	try:
		now = now_datetime()
		breached = frappe.db.get_all(
			"Lab Order",
			filters={
				"docstatus": 1,
				"status": ["in", ["Pending", "In Progress"]],
				"tat_deadline": ["<", now],
			},
			fields=["name"],
		)
		for order in breached:
			frappe.db.set_value("Lab Order", order.name, "priority", "STAT")
		if breached:
			frappe.db.commit()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: check_critical_tat_breach failed")


def flag_expiring_reagents():
	"""Daily: set Reagent Lot status to Expired if past expiry date; warn if expiring in 7 days"""
	try:
		tod = getdate(today())

		# Mark as Expired
		expired = frappe.db.get_all(
			"Reagent Lot",
			filters={"status": "Active", "expiry_date": ["<", tod]},
			fields=["name"],
		)
		for lot in expired:
			frappe.db.set_value("Reagent Lot", lot.name, {"status": "Expired", "days_to_expiry": -1})

		# Update days_to_expiry for all active lots
		active = frappe.db.get_all(
			"Reagent Lot",
			filters={"status": "Active"},
			fields=["name", "expiry_date"],
		)
		for lot in active:
			if lot.expiry_date:
				days = date_diff(lot.expiry_date, tod)
				frappe.db.set_value("Reagent Lot", lot.name, "days_to_expiry", days)

		if expired or active:
			frappe.db.commit()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: flag_expiring_reagents failed")


def flag_expiring_amc():
	"""Daily: publish a desk notification for Analyzers whose AMC expires within 30 days"""
	try:
		tod = getdate(today())
		threshold = add_days(tod, 30)

		analyzers = frappe.db.get_all(
			"Analyzer",
			filters={
				"is_active": 1,
				"amc_expiry_date": ["between", [tod, threshold]],
			},
			fields=["name", "analyzer_name", "amc_expiry_date", "branch"],
		)

		for analyzer in analyzers:
			days_left = date_diff(analyzer.amc_expiry_date, tod)
			frappe.publish_realtime(
				"amc_expiry_alert",
				{
					"message": f"AMC for {analyzer.analyzer_name} expires in {days_left} days",
					"analyzer": analyzer.name,
				},
			)

		# Also flag analyzers with expired AMC
		expired_amc = frappe.db.get_all(
			"Analyzer",
			filters={"is_active": 1, "amc_expiry_date": ["<", tod]},
			fields=["name"],
		)
		for analyzer in expired_amc:
			frappe.db.set_value("Analyzer", analyzer.name, "is_active", 0)

		if expired_amc:
			frappe.db.commit()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: flag_expiring_amc failed")


def flag_expiring_calibrations():
	"""Daily: alert when analyzer calibration is due within 7 days or overdue."""
	try:
		tod = getdate(today())
		threshold = add_days(tod, 7)

		# Calibrations due within 7 days
		due_soon = frappe.db.get_all(
			"Analyzer",
			filters={
				"is_active": 1,
				"next_calibration_due": ["between", [tod, threshold]],
			},
			fields=["name", "analyzer_name", "next_calibration_due", "branch"],
		)

		for analyzer in due_soon:
			days_left = date_diff(analyzer.next_calibration_due, tod)
			frappe.publish_realtime(
				"calibration_due_alert",
				{
					"message": f"Calibration for {analyzer.analyzer_name} is due in {days_left} day(s)",
					"analyzer": analyzer.name,
					"branch": analyzer.branch,
				},
			)

		# Calibrations overdue
		overdue = frappe.db.get_all(
			"Analyzer",
			filters={
				"is_active": 1,
				"next_calibration_due": ["<", tod],
			},
			fields=["name", "analyzer_name", "next_calibration_due"],
		)

		for analyzer in overdue:
			frappe.publish_realtime(
				"calibration_overdue_alert",
				{
					"message": f"Calibration OVERDUE for {analyzer.analyzer_name} (was due {analyzer.next_calibration_due})",
					"analyzer": analyzer.name,
				},
			)

	except Exception:
		frappe.log_error(frappe.get_traceback(), "ArogyaPath: flag_expiring_calibrations failed")
