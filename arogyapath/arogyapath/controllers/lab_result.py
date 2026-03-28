import frappe

def validate(doc, method=None):
	"""Validate lab result and auto-flag values"""
	for item in doc.items:
		item.flag = compute_flag(item)
	
	doc.has_critical_value = any(
		i.flag in ("Critical Low", "Critical High") for i in doc.items
	)

def compute_flag(item):
	"""Compute flag based on reference ranges"""
	if not item.result_numeric:
		return "Normal"
	v = item.result_numeric
	if item.critical_min and v < item.critical_min:
		return "Critical Low"
	if item.critical_max and v > item.critical_max:
		return "Critical High"
	if item.normal_min and v < item.normal_min:
		return "Low"
	if item.normal_max and v > item.normal_max:
		return "High"
	return "Normal"

def on_update(doc, method=None):
	"""Handle result updates"""
	if doc.validation_status == "Pathologist Approved":
		trigger_report_generation(doc)
	if doc.has_critical_value and not doc.critical_notified:
		send_critical_alert(doc)

def trigger_report_generation(doc):
	"""Trigger report generation after pathologist approval"""
	pass

def send_critical_alert(doc):
	"""Send alert for critical values"""
	pass
