// ArogyaPath — Address GST client script
// Mirrors India Compliance's address.js + party.js behaviour:
//   - GSTIN format validation on change
//   - Auto-set gst_category from GSTIN
//   - GSTIN status indicator (● Status: Active / Not Available)
//   - State options restricted to Indian states when country = India

const AP_GST_STATES = [
	"Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh",
	"Assam", "Bihar", "Chandigarh", "Chhattisgarh",
	"Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Goa", "Gujarat",
	"Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand",
	"Karnataka", "Kerala", "Ladakh", "Lakshadweep Islands",
	"Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
	"Nagaland", "Odisha", "Other Countries", "Other Territory",
	"Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
	"Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
];

// Keep in sync with address.py STATE_NUMBERS and custom_fields.py INDIA_STATES

const AP_STATE_NUMBERS = {
	"Andaman and Nicobar Islands": "35", "Andhra Pradesh": "37",
	"Arunachal Pradesh": "12", "Assam": "18", "Bihar": "10",
	"Chandigarh": "04", "Chhattisgarh": "22",
	"Dadra and Nagar Haveli and Daman and Diu": "26", "Delhi": "07",
	"Goa": "30", "Gujarat": "24", "Haryana": "06",
	"Himachal Pradesh": "02", "Jammu and Kashmir": "01",
	"Jharkhand": "20", "Karnataka": "29", "Kerala": "32",
	"Ladakh": "38", "Lakshadweep Islands": "31",
	"Madhya Pradesh": "23", "Maharashtra": "27", "Manipur": "14",
	"Meghalaya": "17", "Mizoram": "15", "Nagaland": "13",
	"Odisha": "21", "Other Countries": "96", "Other Territory": "97",
	"Puducherry": "34", "Punjab": "03", "Rajasthan": "08",
	"Sikkim": "11", "Tamil Nadu": "33", "Telangana": "36",
	"Tripura": "16", "Uttar Pradesh": "09", "Uttarakhand": "05",
	"West Bengal": "19",
};

const GSTIN_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;

// ── GSTIN check-digit validation (Luhn-variant) ──────────────────────────────
const _CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

function _gstin_check_digit(gstin) {
	let total = 0;
	for (let i = 0; i < 14; i++) {
		let val = _CHARS.indexOf(gstin[i]);
		if (i % 2 !== 0) val = val * 2;
		total += Math.floor(val / _CHARS.length) + (val % _CHARS.length);
	}
	return _CHARS[((_CHARS.length - (total % _CHARS.length)) % _CHARS.length)];
}

function ap_validate_gstin(gstin) {
	if (!gstin) return "";
	gstin = gstin.trim().toUpperCase();

	if (gstin.length !== 15) {
		frappe.throw(__("GSTIN must be exactly 15 characters"));
	}
	if (!GSTIN_REGEX.test(gstin)) {
		frappe.throw(__("GSTIN {0} does not match the required format", [`<b>${gstin}</b>`]));
	}
	const expected = _gstin_check_digit(gstin);
	if (gstin[14] !== expected) {
		frappe.throw(__(
			"GSTIN {0} has an invalid check digit. Please verify the GSTIN.",
			[`<b>${gstin}</b>`]
		));
	}
	return gstin;
}

// ── Guess GST Category from GSTIN ────────────────────────────────────────────
function ap_guess_gst_category(gstin, country) {
	if (country && country !== "India") return "Overseas";
	if (!gstin || gstin.length < 6) return "Unregistered";
	gstin = gstin.trim().toUpperCase();
	if (gstin[5] === "C") return "Tax Deductor";
	return "Registered Regular";
}

// ── GSTIN status indicator ────────────────────────────────────────────────────
function ap_set_gstin_status(field) {
	const gstin = field.value;
	if (!gstin || gstin.length !== 15) {
		field.set_description("");
		return;
	}

	frappe.call({
		method: "arogyapath.arogyapath.overrides.address.get_gstin_status",
		args: { gstin },
		callback(r) {
			const data = r.message || {};
			const status = data.status || "Not Available";
			const STATUS_COLORS = {
				"Active": "green",
				"Cancelled": "red",
				"Not Available": "grey",
			};
			const color = STATUS_COLORS[status] || "orange";
			field.set_description(
				`<div class="d-flex indicator ${color}">` +
				`Status:&nbsp;<strong>${__(status)}</strong>` +
				`</div>`
			);
		},
	});
}

// ── Main form event handler ───────────────────────────────────────────────────
frappe.ui.form.on("Address", {
	refresh(frm) {
		// Restrict state field options to Indian states when country = India
		ap_set_state_options(frm);
		// Show GSTIN status on load
		const gstin_field = frm.get_field("gstin");
		if (gstin_field) ap_set_gstin_status(gstin_field);
	},

	country(frm) {
		ap_set_state_options(frm);
		if (!frm.doc.country) return;
		if (frm.doc.country !== "India") {
			frm.set_value("gst_category", "Overseas");
		} else {
			// Re-trigger gstin to re-derive category
			frm.trigger("gstin");
		}
	},

	gstin(frm) {
		let gstin = frm.doc.gstin || "";

		// Only validate when full length typed
		if (gstin && gstin.length === 15) {
			try {
				gstin = ap_validate_gstin(gstin);
				frm.doc.gstin = gstin;
				frm.refresh_field("gstin");
			} catch (e) {
				return;
			}
		}

		// Auto-set GST Category
		const category = ap_guess_gst_category(gstin, frm.doc.country);
		const current = frm.doc.gst_category;
		if (!["SEZ", "Overseas", "Deemed Export", "Registered Composition"].includes(current)) {
			if (current !== category) {
				frm.set_value("gst_category", category);
				frappe.show_alert({
					message: __("GST Category updated to {0}", [`<b>${category}</b>`]),
					indicator: "green",
				});
			}
		}

		// Show GSTIN status indicator
		const gstin_field = frm.get_field("gstin");
		if (gstin_field) ap_set_gstin_status(gstin_field);
	},

	state(frm) {
		// Auto-populate gst_state and gst_state_number from state
		const state = frm.doc.state || "";
		if (state && AP_STATE_NUMBERS[state]) {
			frm.set_value("gst_state", state);
			frm.set_value("gst_state_number", AP_STATE_NUMBERS[state]);
		} else {
			frm.set_value("gst_state", "");
			frm.set_value("gst_state_number", "");
		}
	},
});

function ap_set_state_options(frm) {
	const state_field = frm.fields_dict.state;
	if (!state_field) return;

	const country = (frm.doc.country || "India");
	if (country !== "India") {
		// Clear state options for non-India countries
		frm.set_df_property("state", "options", "");
	} else {
		// Set Indian state options
		frm.set_df_property("state", "options", AP_GST_STATES.join("\n"));
	}
}
