# Copyright (c) 2026, Ascratech and contributors
# Migration script to convert existing Users with lab roles to Employee records

import frappe
from frappe import _


def execute():
	"""
	Migrate existing Users with lab roles to Employee records.
	This is a one-time migration for Phase 10A.
	"""
	frappe.logger().info("Starting migration: Users to Employees")
	
	# Lab roles that we manage
	lab_roles = [
		"Lab Admin",
		"Lab Manager",
		"Lab Pathologist",
		"Lab Technician",
		"Lab Reception"
	]
	
	# Get all enabled System Users
	users = frappe.get_all(
		"User",
		filters={
			"enabled": 1,
			"user_type": "System User",
			"name": ["not in", ["Administrator", "Guest"]]
		},
		fields=["name", "full_name", "email"]
	)
	
	migrated_count = 0
	skipped_count = 0
	
	for user_data in users:
		try:
			# Get User document with roles
			user = frappe.get_doc("User", user_data.name)
			
			# Check if user has any lab roles
			user_lab_roles = [r.role for r in user.roles if r.role in lab_roles]
			
			if not user_lab_roles:
				skipped_count += 1
				continue
			
			# Check if Employee already exists for this user
			if frappe.db.exists("Employee", {"user": user.name}):
				frappe.logger().info(f"Employee already exists for User {user.name}, skipping")
				skipped_count += 1
				continue
			
			# Get default branch (first active branch or create one if none exists)
			default_branch = get_or_create_default_branch()
			
			# Create Employee record
			employee = frappe.new_doc("Employee")
			employee.employee_name = user.full_name or user.name
			employee.user = user.name
			employee.branch = default_branch
			employee.status = "Active"
			employee.is_active = 1
			
			# Set designation based on roles
			if "Lab Pathologist" in user_lab_roles:
				employee.designation = "Pathologist"
			elif "Lab Manager" in user_lab_roles:
				employee.designation = "Lab Manager"
			elif "Lab Technician" in user_lab_roles:
				employee.designation = "Technician"
			elif "Lab Reception" in user_lab_roles:
				employee.designation = "Receptionist"
			elif "Lab Admin" in user_lab_roles:
				employee.designation = "Admin"
			
			# Add roles to Employee
			for role in user_lab_roles:
				employee.append("assigned_roles", {
					"role": role,
					"from_date": frappe.utils.today()
				})
			
			# Disable role sync during migration to avoid circular updates
			employee.flags.ignore_role_sync = True
			employee.insert(ignore_permissions=True)
			
			frappe.logger().info(f"Created Employee {employee.name} for User {user.name}")
			migrated_count += 1
			
		except Exception as e:
			frappe.log_error(
				message=frappe.get_traceback(),
				title=f"Employee Migration Failed for User {user_data.name}"
			)
			frappe.logger().error(f"Failed to migrate User {user_data.name}: {str(e)}")
	
	frappe.db.commit()
	
	frappe.logger().info(
		f"Migration completed: {migrated_count} users migrated, {skipped_count} skipped"
	)
	
	return {
		"migrated": migrated_count,
		"skipped": skipped_count
	}


def get_or_create_default_branch():
	"""Get the first active branch or create a default one"""
	# Try to get existing branch
	branch = frappe.db.get_value(
		"Lab Branch",
		{"is_active": 1},
		"name",
		order_by="is_head_office desc, creation asc"
	)
	
	if branch:
		return branch
	
	# Create default branch if none exists
	frappe.logger().info("No active branch found, creating default branch")
	
	default_branch = frappe.new_doc("Lab Branch")
	default_branch.branch_name = "Main Branch"
	default_branch.branch_code = "MAIN"
	default_branch.is_head_office = 1
	default_branch.is_active = 1
	default_branch.insert(ignore_permissions=True)
	
	return default_branch.name
