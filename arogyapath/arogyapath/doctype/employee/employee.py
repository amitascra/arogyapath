# Copyright (c) 2026, Ascratech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Employee(Document):
	def validate(self):
		"""Validate employee data before saving"""
		self.validate_user_link()
		self.validate_pathologist_signature()
		self.set_company_email()
	
	def on_update(self):
		"""Sync roles to User after save"""
		if not self.flags.ignore_role_sync:
			self.sync_roles_to_user()
	
	def validate_user_link(self):
		"""Ensure User exists and is not already linked to another Employee"""
		if not self.user:
			frappe.throw(_("User is mandatory"))
		
		# Check if User exists
		if not frappe.db.exists("User", self.user):
			frappe.throw(_("User {0} does not exist").format(self.user))
		
		# Check if User is already linked to another Employee
		existing = frappe.db.get_value(
			"Employee",
			{"user": self.user, "name": ["!=", self.name or ""]},
			"name"
		)
		if existing:
			frappe.throw(
				_("User {0} is already linked to Employee {1}").format(
					self.user, existing
				)
			)
	
	def set_company_email(self):
		"""Fetch company email from User"""
		if self.user:
			self.company_email = frappe.db.get_value("User", self.user, "email")
	
	def validate_pathologist_signature(self):
		"""Pathologists should have signature for report signing"""
		if not self.assigned_roles:
			return
		
		# Check if Lab Pathologist role is assigned
		has_pathologist_role = any(
			role.role == "Lab Pathologist" 
			for role in self.assigned_roles
			if not role.to_date or getdate(role.to_date) >= getdate()
		)
		
		if has_pathologist_role and not self.signature_image:
			frappe.msgprint(
				_("Pathologist should have a signature image for reports"),
				indicator="orange",
				alert=True
			)
	
	def sync_roles_to_user(self):
		"""Sync assigned_roles to User DocType"""
		if not self.user:
			return
		
		try:
			user = frappe.get_doc("User", self.user)
			
			# Lab-related roles that we manage
			lab_roles = [
				"Lab Admin",
				"Lab Manager",
				"Lab Pathologist",
				"Lab Technician",
				"Lab Reception"
			]
			
			# Remove all lab-related roles from User first
			user.roles = [r for r in user.roles if r.role not in lab_roles]
			
			# Add active roles from Employee
			for role_row in self.assigned_roles:
				# Check if role is currently active (no to_date or to_date is in future)
				if not role_row.to_date or getdate(role_row.to_date) >= getdate():
					# Check if role already exists in user.roles
					if not any(r.role == role_row.role for r in user.roles):
						user.append("roles", {"role": role_row.role})
			
			# Save User document
			user.flags.ignore_permissions = True
			user.save()
			
			frappe.logger().info(
				f"Employee {self.name}: Synced roles to User {self.user}"
			)
			
		except Exception as e:
			frappe.log_error(
				message=frappe.get_traceback(),
				title=f"Employee Role Sync Failed: {self.name}"
			)
			frappe.throw(
				_("Failed to sync roles to User {0}. Error: {1}").format(
					self.user, str(e)
				)
			)
	
	def on_trash(self):
		"""Remove lab roles from User when Employee is deleted"""
		if self.user:
			try:
				user = frappe.get_doc("User", self.user)
				
				lab_roles = [
					"Lab Admin",
					"Lab Manager",
					"Lab Pathologist",
					"Lab Technician",
					"Lab Reception"
				]
				
				# Remove all lab roles
				user.roles = [r for r in user.roles if r.role not in lab_roles]
				user.flags.ignore_permissions = True
				user.save()
				
			except Exception:
				frappe.log_error(
					message=frappe.get_traceback(),
					title=f"Employee Role Cleanup Failed: {self.name}"
				)
