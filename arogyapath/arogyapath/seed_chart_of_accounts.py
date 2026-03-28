# Copyright (c) 2026, Ascratech and contributors
# Seed Chart of Accounts for Pathology Lab

import frappe
from frappe import _


def get_default_lab():
	"""Get default pathology lab from settings"""
	return frappe.db.get_single_value("Lab Settings", "default_lab")

def seed_chart_of_accounts(pathology_lab=None):
	"""Seed default Chart of Accounts for pathology lab"""
	frappe.logger().info("Seeding Chart of Accounts...")
	
	# Get default pathology lab if not provided
	if not pathology_lab:
		pathology_lab = frappe.db.get_single_value("Lab Settings", "default_lab")
		if not pathology_lab:
			frappe.logger().warning("No default Pathology Lab found. Skipping Chart of Accounts seeding.")
			frappe.logger().warning("Please create a Pathology Lab and run: bench --site [sitename] execute arogyapath.arogyapath.seed_chart_of_accounts.execute")
			return
	
	accounts = [
		# Assets
		{"account_name": "Assets", "root_type": "Asset", "is_group": 1},
		{"account_name": "Current Assets", "root_type": "Asset", "parent_account": "Assets", "is_group": 1},
		{"account_name": "Cash", "root_type": "Asset", "parent_account": "Current Assets", "account_type": "Cash", "is_group": 1},
		{"account_name": "Cash - Main Branch", "root_type": "Asset", "parent_account": "Cash", "account_type": "Cash"},
		{"account_name": "Bank Accounts", "root_type": "Asset", "parent_account": "Current Assets", "account_type": "Bank", "is_group": 1},
		{"account_name": "Bank - HDFC", "root_type": "Asset", "parent_account": "Bank Accounts", "account_type": "Bank"},
		{"account_name": "Accounts Receivable", "root_type": "Asset", "parent_account": "Current Assets", "account_type": "Receivable", "is_group": 1},
		{"account_name": "Debtors - Patients", "root_type": "Asset", "parent_account": "Accounts Receivable", "account_type": "Receivable"},
		{"account_name": "Debtors - Corporate", "root_type": "Asset", "parent_account": "Accounts Receivable", "account_type": "Receivable"},
		{"account_name": "Stock Assets", "root_type": "Asset", "parent_account": "Current Assets", "account_type": "Stock", "is_group": 1},
		{"account_name": "Reagent Stock", "root_type": "Asset", "parent_account": "Stock Assets", "account_type": "Stock"},
		{"account_name": "Consumables Stock", "root_type": "Asset", "parent_account": "Stock Assets", "account_type": "Stock"},
		{"account_name": "Fixed Assets", "root_type": "Asset", "parent_account": "Assets", "account_type": "Fixed Asset", "is_group": 1},
		{"account_name": "Equipment", "root_type": "Asset", "parent_account": "Fixed Assets", "account_type": "Fixed Asset"},
		
		# Liabilities
		{"account_name": "Liabilities", "root_type": "Liability", "is_group": 1},
		{"account_name": "Current Liabilities", "root_type": "Liability", "parent_account": "Liabilities", "is_group": 1},
		{"account_name": "Accounts Payable", "root_type": "Liability", "parent_account": "Current Liabilities", "account_type": "Payable", "is_group": 1},
		{"account_name": "Creditors - Suppliers", "root_type": "Liability", "parent_account": "Accounts Payable", "account_type": "Payable"},
		{"account_name": "Tax Liabilities", "root_type": "Liability", "parent_account": "Current Liabilities", "account_type": "Tax", "is_group": 1},
		{"account_name": "Output CGST @ 9%", "root_type": "Liability", "parent_account": "Tax Liabilities", "account_type": "Tax"},
		{"account_name": "Output SGST @ 9%", "root_type": "Liability", "parent_account": "Tax Liabilities", "account_type": "Tax"},
		{"account_name": "Output IGST @ 18%", "root_type": "Liability", "parent_account": "Tax Liabilities", "account_type": "Tax"},
		{"account_name": "Output Cess", "root_type": "Liability", "parent_account": "Tax Liabilities", "account_type": "Tax"},
		{"account_name": "TDS Payable", "root_type": "Liability", "parent_account": "Tax Liabilities", "account_type": "Tax"},
		
		# Equity
		{"account_name": "Equity", "root_type": "Equity", "is_group": 1},
		{"account_name": "Capital Account", "root_type": "Equity", "parent_account": "Equity"},
		{"account_name": "Retained Earnings", "root_type": "Equity", "parent_account": "Equity"},
		
		# Income
		{"account_name": "Income", "root_type": "Income", "is_group": 1},
		{"account_name": "Direct Income", "root_type": "Income", "parent_account": "Income", "is_group": 1},
		{"account_name": "Lab Service Income", "root_type": "Income", "parent_account": "Direct Income", "account_type": "Income"},
		{"account_name": "Other Income", "root_type": "Income", "parent_account": "Income", "is_group": 1},
		
		# Expenses
		{"account_name": "Expenses", "root_type": "Expense", "is_group": 1},
		{"account_name": "Direct Expenses", "root_type": "Expense", "parent_account": "Expenses", "is_group": 1},
		{"account_name": "Cost of Goods Sold", "root_type": "Expense", "parent_account": "Direct Expenses", "account_type": "Cost of Goods Sold"},
		{"account_name": "Reagent Expenses", "root_type": "Expense", "parent_account": "Direct Expenses"},
		{"account_name": "Doctor Commission", "root_type": "Expense", "parent_account": "Direct Expenses"},
		{"account_name": "Indirect Expenses", "root_type": "Expense", "parent_account": "Expenses", "is_group": 1},
		{"account_name": "Salary Expenses", "root_type": "Expense", "parent_account": "Indirect Expenses"},
		{"account_name": "Rent Expenses", "root_type": "Expense", "parent_account": "Indirect Expenses"},
		{"account_name": "Utility Expenses", "root_type": "Expense", "parent_account": "Indirect Expenses"},
		{"account_name": "Input Tax Credit", "root_type": "Expense", "parent_account": "Expenses", "is_group": 1},
		{"account_name": "Input CGST @ 9%", "root_type": "Expense", "parent_account": "Input Tax Credit", "account_type": "Tax"},
		{"account_name": "Input SGST @ 9%", "root_type": "Expense", "parent_account": "Input Tax Credit", "account_type": "Tax"},
		{"account_name": "Input IGST @ 18%", "root_type": "Expense", "parent_account": "Input Tax Credit", "account_type": "Tax"},
		{"account_name": "Input Cess", "root_type": "Expense", "parent_account": "Input Tax Credit", "account_type": "Tax"},
	]
	
	for acc_data in accounts:
		# Add pathology_lab to account data
		acc_data["pathology_lab"] = pathology_lab
		
		# Check if account exists for this pathology lab
		existing = frappe.db.exists("Account", {
			"account_name": acc_data["account_name"],
			"pathology_lab": pathology_lab
		})
		
		if not existing:
			acc = frappe.new_doc("Account")
			acc.update(acc_data)
			acc.insert(ignore_permissions=True)
			frappe.logger().info(f"Created Account: {acc.account_name} for {pathology_lab}")
		else:
			frappe.logger().info(f"Account already exists: {acc_data['account_name']} for {pathology_lab}")
	
	frappe.db.commit()


def execute():
	"""Main execution function"""
	frappe.logger().info("=" * 60)
	frappe.logger().info("Starting Chart of Accounts Seeding")
	frappe.logger().info("=" * 60)
	
	seed_chart_of_accounts()
	
	frappe.logger().info("=" * 60)
	frappe.logger().info("Chart of Accounts Seeding Completed")
	frappe.logger().info("=" * 60)
