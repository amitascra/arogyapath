# Copyright (c) 2026, Ascratech and contributors
# Seed default tax templates and TDS categories

import frappe
from frappe import _


def seed_tax_withholding_categories():
	"""Seed common TDS categories as per Indian Income Tax Act"""
	frappe.logger().info("Seeding Tax Withholding Categories...")
	
	categories = [
		{
			"category_name": "194C - Contractor",
			"section_code": "194C",
			"rate": 1.0,
			"threshold_amount": 30000,
			"description": "Payment to contractors and sub-contractors. TDS @ 1% if PAN available, 2% otherwise.",
			"is_active": 1
		},
		{
			"category_name": "194J - Professional Services",
			"section_code": "194J",
			"rate": 10.0,
			"threshold_amount": 30000,
			"description": "Fees for professional or technical services. TDS @ 10%.",
			"is_active": 1
		},
		{
			"category_name": "194H - Commission",
			"section_code": "194H",
			"rate": 5.0,
			"threshold_amount": 15000,
			"description": "Commission or brokerage payments. TDS @ 5%.",
			"is_active": 1
		},
		{
			"category_name": "194I - Rent",
			"section_code": "194I",
			"rate": 10.0,
			"threshold_amount": 240000,
			"description": "Rent for land, building, or furniture. TDS @ 10% for machinery/equipment, 2% for land/building.",
			"is_active": 1
		},
		{
			"category_name": "194Q - Purchase of Goods",
			"section_code": "194Q",
			"rate": 0.1,
			"threshold_amount": 5000000,
			"description": "Purchase of goods exceeding Rs. 50 lakhs in a year. TDS @ 0.1%.",
			"is_active": 1
		}
	]
	
	for cat_data in categories:
		if not frappe.db.exists("Tax Withholding Category", cat_data["category_name"]):
			cat = frappe.new_doc("Tax Withholding Category")
			cat.update(cat_data)
			cat.insert(ignore_permissions=True)
			frappe.logger().info(f"Created Tax Withholding Category: {cat.category_name}")
		else:
			frappe.logger().info(f"Tax Withholding Category already exists: {cat_data['category_name']}")
	
	frappe.db.commit()


def seed_sales_tax_templates():
	"""Seed common GST templates for sales (Lab Invoices)"""
	frappe.logger().info("Seeding Sales Tax Templates...")
	
	templates = [
		{
			"title": "GST 18% Intrastate",
			"is_default": 1,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Output CGST",
					"description": "CGST @ 9%",
					"rate": 9.0
				},
				{
					"charge_type": "On Net Total",
					"account_head": "Output SGST",
					"description": "SGST @ 9%",
					"rate": 9.0
				}
			]
		},
		{
			"title": "GST 18% Interstate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Output IGST",
					"description": "IGST @ 18%",
					"rate": 18.0
				}
			]
		},
		{
			"title": "GST 12% Intrastate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Output CGST",
					"description": "CGST @ 6%",
					"rate": 6.0
				},
				{
					"charge_type": "On Net Total",
					"account_head": "Output SGST",
					"description": "SGST @ 6%",
					"rate": 6.0
				}
			]
		},
		{
			"title": "GST 12% Interstate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Output IGST",
					"description": "IGST @ 12%",
					"rate": 12.0
				}
			]
		}
	]
	
	for tmpl_data in templates:
		if not frappe.db.exists("Sales Taxes and Charges Template", tmpl_data["title"]):
			tmpl = frappe.new_doc("Sales Taxes and Charges Template")
			tmpl.title = tmpl_data["title"]
			tmpl.is_default = tmpl_data["is_default"]
			
			for tax_row in tmpl_data["taxes"]:
				tmpl.append("taxes", tax_row)
			
			tmpl.insert(ignore_permissions=True)
			frappe.logger().info(f"Created Sales Tax Template: {tmpl.title}")
		else:
			frappe.logger().info(f"Sales Tax Template already exists: {tmpl_data['title']}")
	
	frappe.db.commit()


def seed_purchase_tax_templates():
	"""Seed common GST templates for purchases"""
	frappe.logger().info("Seeding Purchase Tax Templates...")
	
	templates = [
		{
			"title": "Input GST 18% Intrastate",
			"is_default": 1,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Input CGST",
					"description": "Input CGST @ 9%",
					"rate": 9.0
				},
				{
					"charge_type": "On Net Total",
					"account_head": "Input SGST",
					"description": "Input SGST @ 9%",
					"rate": 9.0
				}
			]
		},
		{
			"title": "Input GST 18% Interstate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Input IGST",
					"description": "Input IGST @ 18%",
					"rate": 18.0
				}
			]
		},
		{
			"title": "Input GST 12% Intrastate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Input CGST",
					"description": "Input CGST @ 6%",
					"rate": 6.0
				},
				{
					"charge_type": "On Net Total",
					"account_head": "Input SGST",
					"description": "Input SGST @ 6%",
					"rate": 6.0
				}
			]
		},
		{
			"title": "Input GST 12% Interstate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Input IGST",
					"description": "Input IGST @ 12%",
					"rate": 12.0
				}
			]
		},
		{
			"title": "Input GST 5% Intrastate",
			"is_default": 0,
			"taxes": [
				{
					"charge_type": "On Net Total",
					"account_head": "Input CGST",
					"description": "Input CGST @ 2.5%",
					"rate": 2.5
				},
				{
					"charge_type": "On Net Total",
					"account_head": "Input SGST",
					"description": "Input SGST @ 2.5%",
					"rate": 2.5
				}
			]
		}
	]
	
	for tmpl_data in templates:
		if not frappe.db.exists("Purchase Taxes and Charges Template", tmpl_data["title"]):
			tmpl = frappe.new_doc("Purchase Taxes and Charges Template")
			tmpl.title = tmpl_data["title"]
			tmpl.is_default = tmpl_data["is_default"]
			
			for tax_row in tmpl_data["taxes"]:
				tmpl.append("taxes", tax_row)
			
			tmpl.insert(ignore_permissions=True)
			frappe.logger().info(f"Created Purchase Tax Template: {tmpl.title}")
		else:
			frappe.logger().info(f"Purchase Tax Template already exists: {tmpl_data['title']}")
	
	frappe.db.commit()


def execute():
	"""Main execution function"""
	frappe.logger().info("=" * 60)
	frappe.logger().info("Starting Tax Templates Seeding")
	frappe.logger().info("=" * 60)
	
	seed_tax_withholding_categories()
	seed_sales_tax_templates()
	seed_purchase_tax_templates()
	
	frappe.logger().info("=" * 60)
	frappe.logger().info("Tax Templates Seeding Completed")
	frappe.logger().info("=" * 60)
