# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CASettings(Document):
	def validate(self):
		"""Validate settings"""
		# Check WhatsApp instance status if enabled
		if self.enable_whatsapp_notifications and self.whatsapp_instance:
			self.update_whatsapp_instance_status()
	
	def update_whatsapp_instance_status(self):
		"""Update WhatsApp instance status"""
		try:
			instance = frappe.get_doc("WhatsApp Instance", self.whatsapp_instance)
			self.whatsapp_instance_status = instance.status
		except Exception as e:
			frappe.log_error(f"Error updating WhatsApp instance status: {str(e)}")
			self.whatsapp_instance_status = "Unknown"
