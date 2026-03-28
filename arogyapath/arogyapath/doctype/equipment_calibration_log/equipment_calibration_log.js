// Copyright (c) 2026, Ascratech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment Calibration Log", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Analyzer"), () => {
				frappe.set_route("Form", "Analyzer", frm.doc.analyzer);
			});
		}
	},

	calibration_date(frm) {
		if (frm.doc.calibration_date) {
			const due = frappe.datetime.add_months(frm.doc.calibration_date, 12);
			frm.set_value("next_due_date", due);
		}
	},

	calibration_result(frm) {
		if (frm.doc.calibration_result === "Fail") {
			frappe.msgprint({
				title: __("Action Required"),
				message: __("Calibration FAILED. Analyzer should be taken out of service until recalibrated."),
				indicator: "red",
			});
		}
	},
});
