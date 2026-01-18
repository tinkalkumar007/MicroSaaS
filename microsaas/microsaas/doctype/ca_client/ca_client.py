# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CAClient(Document):
	def validate(self):
		"""Validate client data before saving"""
		# Ensure WhatsApp number is provided if WhatsApp notifications are enabled
		if not self.whatsapp_number and frappe.db.get_single_value("CA Settings", "enable_whatsapp_notifications"):
			frappe.msgprint("WhatsApp number is recommended for receiving notifications")
		
		# Validate email format
		if self.email and "@" not in self.email:
			frappe.throw("Invalid email address")
	
	def on_update(self):
		"""Actions to perform after client is updated"""
		# Create portal user if portal access is enabled and user doesn't exist
		if self.portal_access_enabled and not frappe.db.exists("User", self.email):
			self.create_portal_user()
	
	def create_portal_user(self):
		"""Create a portal user for the client"""
		try:
			user = frappe.get_doc({
				"doctype": "User",
				"email": self.email,
				"first_name": self.client_name,
				"enabled": 1,
				"user_type": "Website User",
				"send_welcome_email": 1
			})
			user.insert(ignore_permissions=True)
			user.add_roles("Customer")  # Add customer role for portal access
			frappe.msgprint(f"Portal user created for {self.client_name}")
		except Exception as e:
			frappe.log_error(f"Error creating portal user: {str(e)}")
