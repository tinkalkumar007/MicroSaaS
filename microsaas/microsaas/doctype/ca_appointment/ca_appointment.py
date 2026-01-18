# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime
from datetime import timedelta


class CAAppointment(Document):
	def validate(self):
		"""Validate appointment data"""
		# Check if appointment is in the past
		appointment_datetime = get_datetime(f"{self.appointment_date} {self.appointment_time}")
		if appointment_datetime < now_datetime():
			frappe.msgprint("Warning: Appointment is scheduled in the past")
		
		# Set CA name
		if self.assigned_ca:
			self.ca_name = frappe.db.get_value("User", self.assigned_ca, "full_name")
			
		# Auto-set firm from client
		if self.client and not self.firm:
			self.firm = frappe.db.get_value("CA Client", self.client, "firm")
	
	def on_submit(self):
		"""Actions after appointment is confirmed"""
		if self.send_reminder:
			self.schedule_reminder()
	
	def schedule_reminder(self):
		"""Schedule appointment reminder"""
		# Reminder will be sent by the scheduler service
		# based on reminder_time setting
		pass
	
	def cancel_appointment(self, reason=None):
		"""Cancel appointment and notify client"""
		self.status = "Cancelled"
		self.notes = f"{self.notes}\n\nCancellation Reason: {reason}" if reason else self.notes
		self.save()
		
		# Send cancellation notification
		try:
			from microsaas.microsaas.services.notification_service import send_notification
			
			notification_data = {
				"client_name": self.client_name,
				"appointment_date": self.appointment_date,
				"appointment_time": self.appointment_time,
				"ca_name": self.ca_name,
				"reason": reason or "Not specified"
			}
			
			send_notification(
				client=self.client,
				template_type="appointment_cancelled",
				data=notification_data
			)
		except Exception as e:
			frappe.log_error(f"Error sending cancellation notification: {str(e)}")
