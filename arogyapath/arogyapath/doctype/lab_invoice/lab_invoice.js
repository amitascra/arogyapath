// Copyright (c) 2026, Amit Kumar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Invoice', {
	onload: function(frm) {
		// Set place_of_supply options
		frm.set_df_property('place_of_supply', 'options', get_place_of_supply_options());
	},

	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			if (frm.doc.outstanding_amount > 0) {
				// Payment Entry button (ERPNext standard)
				frm.add_custom_button(__('Payment'), function() {
					frappe.call({
						method: 'arogyapath.arogyapath.doctype.lab_invoice.lab_invoice_payment.get_payment_entry',
						args: {
							lab_invoice_name: frm.doc.name
						},
						callback: function(r) {
							if (!r.exc) {
								var doc = frappe.model.sync(r.message);
								frappe.set_route('Form', doc[0].doctype, doc[0].name);
							}
						}
					});
				}, __('Create'));
				
				// Payment Request button (for online payments)
				frm.add_custom_button(__('Payment Request'), function() {
					frappe.call({
						method: 'erpnext.accounts.doctype.payment_request.payment_request.make_payment_request',
						args: {
							dt: frm.doc.doctype,
							dn: frm.doc.name,
							recipient_id: frm.doc.contact_email,
							payment_request_type: 'Inward',
							party_type: 'Customer',
							party: frm.doc.patient,
							party_name: frm.doc.patient_name
						},
						callback: function(r) {
							if (!r.exc) {
								frappe.model.sync(r.message);
								frappe.set_route('Form', r.message.doctype, r.message.name);
							}
						}
					});
				}, __('Create'));
				
				// Set Create button group as primary
				frm.page.set_inner_btn_group_as_primary(__('Create'));
			}

			frm.add_custom_button(__('Send Invoice'), function() {
				frappe.set_route('print', frm.doc.doctype, frm.doc.name);
			});
		}

		// Auto-populate items from Lab Order
		if (frm.is_new() && frm.doc.lab_order) {
			frm.trigger('lab_order');
		}

		// Render address displays
		frm.trigger('render_address_display');
		frm.trigger('render_company_address_display');
	},

	patient: function(frm) {
		// Instantly fetch all GST details when patient is selected
		if (frm.doc.patient && frm.doc.pathology_lab) {
			fetch_gst_details(frm);
		}
	},

	branch: function(frm) {
		// Branch changed - fetch pathology lab
		if (frm.doc.branch && !frm.doc.pathology_lab) {
			frappe.db.get_value('Lab Branch', frm.doc.branch, 'pathology_lab')
				.then(r => {
					if (r.message && r.message.pathology_lab) {
						frm.set_value('pathology_lab', r.message.pathology_lab);
					}
				});
		}
	},

	pathology_lab: function(frm) {
		// Instantly fetch all GST details when pathology lab is selected
		if (frm.doc.patient && frm.doc.pathology_lab) {
			fetch_gst_details(frm);
		}
	},

	customer_address: function(frm) {
		// Render address display when address changes
		frm.trigger('render_address_display');
	},

	company_address: function(frm) {
		// Render company address display when address changes
		frm.trigger('render_company_address_display');
	},

	render_address_display: function(frm) {
		if (frm.doc.customer_address) {
			frappe.call({
				method: 'frappe.contacts.doctype.address.address.get_address_display',
				args: { address_dict: frm.doc.customer_address },
				callback: function(r) {
					if (r.message) {
						frm.set_value('address_display', r.message);
					}
				}
			});
		} else {
			frm.set_value('address_display', '');
		}
	},

	render_company_address_display: function(frm) {
		if (frm.doc.company_address) {
			frappe.call({
				method: 'frappe.contacts.doctype.address.address.get_address_display',
				args: { address_dict: frm.doc.company_address },
				callback: function(r) {
					if (r.message) {
						frm.set_value('company_address_display', r.message);
					}
				}
			});
		} else {
			frm.set_value('company_address_display', '');
		}
	},

	lab_order: function(frm) {
		if (frm.doc.lab_order) {
			frappe.db.get_doc('Lab Order', frm.doc.lab_order).then(function(order) {
				frm.clear_table('items');
				order.tests.forEach(function(t) {
					if (t.status !== 'Cancelled') {
						let row = frm.add_child('items');
						row.test = t.test;
						row.test_name = t.test_name;
						row.mrp = t.rate;
						row.rate = t.rate;
						row.department = t.department;
					}
				});
				frm.refresh_field('items');
				frm.trigger('calculate_totals');
			});
		}
	},

	amount_paid: function(frm) {
		frm.trigger('calculate_totals');
	},

	discount_scheme: function(frm) {
		frm.save();
	},

	corporate_account: function(frm) {
		frm.save();
	},

	calculate_totals: function(frm) {
		let gross = 0, tax = 0;
		(frm.doc.items || []).forEach(function(item) {
			gross += flt(item.mrp);
			tax += flt(item.tax_amount);
		});
		frm.set_value('gross_amount', gross);
		let outstanding = flt(frm.doc.grand_total) - flt(frm.doc.amount_paid);
		frm.set_value('outstanding_amount', outstanding > 0 ? outstanding : 0);
	}
});

// Fetch all GST details instantly (addresses, GSTIN, place of supply, taxes)
function fetch_gst_details(frm) {
	if (!frm.doc.patient || !frm.doc.pathology_lab) {
		return;
	}
	
	frappe.call({
		method: 'arogyapath.arogyapath.controllers.lab_invoice.get_patient_gst_details',
		args: {
			patient: frm.doc.patient,
			pathology_lab: frm.doc.pathology_lab
		},
		callback: function(r) {
			if (r.message) {
				const gst_details = r.message;
				
				// Set address fields
				if (gst_details.customer_address) {
					frm.set_value('customer_address', gst_details.customer_address);
				}
				if (gst_details.company_address) {
					frm.set_value('company_address', gst_details.company_address);
				}
				
				// Set GSTIN fields
				if (gst_details.billing_address_gstin !== undefined) {
					frm.set_value('billing_address_gstin', gst_details.billing_address_gstin);
				}
				if (gst_details.company_gstin !== undefined) {
					frm.set_value('company_gstin', gst_details.company_gstin);
				}
				
				// Set GST category and place of supply
				if (gst_details.gst_category) {
					frm.set_value('gst_category', gst_details.gst_category);
				}
				if (gst_details.place_of_supply) {
					frm.set_value('place_of_supply', gst_details.place_of_supply);
				}
				
				// Set tax category
				if (gst_details.tax_category) {
					frm.set_value('tax_category', gst_details.tax_category);
				}
				
				// Set contact fields
				if (gst_details.contact_person) {
					frm.set_value('contact_person', gst_details.contact_person);
				}
				if (gst_details.contact_display) {
					frm.set_value('contact_display', gst_details.contact_display);
				}
				if (gst_details.contact_mobile) {
					frm.set_value('contact_mobile', gst_details.contact_mobile);
				}
				if (gst_details.contact_email) {
					frm.set_value('contact_email', gst_details.contact_email);
				}
				if (gst_details.company_contact_person) {
					frm.set_value('company_contact_person', gst_details.company_contact_person);
				}
				
				// Set tax template and tax rows
				if (gst_details.taxes_and_charges) {
					frm.set_value('taxes_and_charges', gst_details.taxes_and_charges);
				}
				
				if (gst_details.taxes && gst_details.taxes.length > 0) {
					frm.clear_table('taxes');
					gst_details.taxes.forEach(function(tax) {
						let row = frm.add_child('taxes');
						row.charge_type = tax.charge_type;
						row.account_head = tax.account_head;
						row.rate = tax.rate;
						row.description = tax.description;
						row.gst_tax_type = tax.gst_tax_type;
					});
					frm.refresh_field('taxes');
				}
				
				// Trigger address display rendering
				frm.trigger('render_address_display');
				frm.trigger('render_company_address_display');
			}
		}
	});
}

frappe.ui.form.on('Lab Invoice Item', {
	mrp: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'rate', flt(row.mrp) - flt(row.discount_amount));
	},
	discount_amount: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'rate', flt(row.mrp) - flt(row.discount_amount));
	}
});

// Helper function to get place of supply options (all Indian states)
function get_place_of_supply_options() {
	return [
		"01-Jammu and Kashmir",
		"02-Himachal Pradesh",
		"03-Punjab",
		"04-Chandigarh",
		"05-Uttarakhand",
		"06-Haryana",
		"07-Delhi",
		"08-Rajasthan",
		"09-Uttar Pradesh",
		"10-Bihar",
		"11-Sikkim",
		"12-Arunachal Pradesh",
		"13-Nagaland",
		"14-Manipur",
		"15-Mizoram",
		"16-Tripura",
		"17-Meghalaya",
		"18-Assam",
		"19-West Bengal",
		"20-Jharkhand",
		"21-Odisha",
		"22-Chhattisgarh",
		"23-Madhya Pradesh",
		"24-Gujarat",
		"26-Dadra and Nagar Haveli and Daman and Diu",
		"27-Maharashtra",
		"29-Karnataka",
		"30-Goa",
		"31-Lakshadweep",
		"32-Kerala",
		"33-Tamil Nadu",
		"34-Puducherry",
		"35-Andaman and Nicobar Islands",
		"36-Telangana",
		"37-Andhra Pradesh",
		"38-Ladakh",
		"97-Other Territory"
	];
}
