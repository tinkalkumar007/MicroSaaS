# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
Reminder Scheduler Service
Automated reminders for invoices, payments, appointments, and tax deadlines
"""

import frappe
from frappe.utils import today, add_days, getdate, add_months
from datetime import datetime, timedelta


def send_invoice_reminders():
	"""Send invoice payment reminders based on due dates"""
	try:
		# Get all unpaid and overdue invoices
		invoices = frappe.get_all(
			"CA Invoice",
			filters={
				"status": ["in", ["Unpaid", "Partially Paid", "Overdue"]],
				"docstatus": 1
			},
			fields=["name", "client", "client_name", "total_amount", "due_date", "status"]
		)
		
		for invoice_data in invoices:
			invoice = frappe.get_doc("CA Invoice", invoice_data.name)
			days_until_due = (getdate(invoice.due_date) - getdate(today())).days
			
			# Send reminder based on schedule
			if days_until_due == 3:
				# 3 days before due date
				send_reminder(invoice, "payment_reminder", days_until_due)
			elif days_until_due == 0:
				# On due date
				send_reminder(invoice, "payment_reminder", days_until_due)
			elif days_until_due < 0:
				# Overdue
				days_overdue = abs(days_until_due)
				if days_overdue in [3, 7, 14, 30]:  # Send on specific overdue days
					send_reminder(invoice, "payment_overdue", days_overdue)
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error sending invoice reminders: {str(e)}", "Invoice Reminder Error")


def send_reminder(invoice, template_type, days):
	"""Send reminder notification"""
	try:
		from microsaas.microsaas.services.notification_service import send_notification
		
		# Prepare notification data
		notification_data = {
			"client_name": invoice.client_name,
			"invoice_number": invoice.name,
			"amount": invoice.total_amount,
			"due_date": invoice.due_date,
			"portal_link": invoice.portal_link,
			"days_overdue": days if template_type == "payment_overdue" else 0,
			"days_until_due": days if template_type == "payment_reminder" else 0
		}
		
		# Send notification
		send_notification(
			client=invoice.client,
			template_type=template_type,
			data=notification_data
		)
		
	except Exception as e:
		frappe.log_error(f"Error sending reminder for invoice {invoice.name}: {str(e)}")


def send_appointment_reminders():
	"""Send appointment reminders 24 hours and 1 hour before"""
	try:
		# Get appointments scheduled for tomorrow (24 hour reminder)
		tomorrow = add_days(today(), 1)
		appointments_tomorrow = frappe.get_all(
			"CA Appointment",
			filters={
				"appointment_date": tomorrow,
				"status": "Scheduled"
			},
			fields=["name", "client", "appointment_date", "appointment_time", "assigned_ca"]
		)
		
		for apt in appointments_tomorrow:
			send_appointment_reminder(apt, hours_before=24)
		
		# Get appointments in the next hour (1 hour reminder)
		now = datetime.now()
		one_hour_later = now + timedelta(hours=1)
		
		appointments_soon = frappe.get_all(
			"CA Appointment",
			filters={
				"appointment_date": today(),
				"status": "Scheduled"
			},
			fields=["name", "client", "appointment_date", "appointment_time", "assigned_ca"]
		)
		
		for apt in appointments_soon:
			# Check if appointment is within next hour
			apt_datetime = datetime.combine(getdate(apt.appointment_date), apt.appointment_time)
			if now < apt_datetime <= one_hour_later:
				send_appointment_reminder(apt, hours_before=1)
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error sending appointment reminders: {str(e)}", "Appointment Reminder Error")


def send_appointment_reminder(appointment, hours_before):
	"""Send appointment reminder notification"""
	try:
		from microsaas.microsaas.services.notification_service import send_notification
		
		apt_doc = frappe.get_doc("CA Appointment", appointment.name)
		ca_name = frappe.db.get_value("User", apt_doc.assigned_ca, "full_name")
		
		notification_data = {
			"client_name": frappe.db.get_value("CA Client", apt_doc.client, "client_name"),
			"appointment_date": apt_doc.appointment_date,
			"appointment_time": apt_doc.appointment_time,
			"ca_name": ca_name,
			"hours_before": hours_before
		}
		
		send_notification(
			client=apt_doc.client,
			template_type="appointment_reminder",
			data=notification_data
		)
		
	except Exception as e:
		frappe.log_error(f"Error sending appointment reminder: {str(e)}")


def check_tax_deadlines():
	"""Check and send tax deadline reminders"""
	try:
		# Indian tax deadlines (customize as needed)
		tax_deadlines = {
			"2026-07-31": "ITR Filing Deadline for Individuals",
			"2026-10-31": "ITR Filing Deadline for Audit Cases",
			"2026-03-31": "Financial Year End",
			"2026-06-15": "Advance Tax Q1",
			"2026-09-15": "Advance Tax Q2",
			"2026-12-15": "Advance Tax Q3",
			"2026-03-15": "Advance Tax Q4"
		}
		
		# Send reminders 7 days and 1 day before deadline
		for deadline_date, deadline_name in tax_deadlines.items():
			days_until = (getdate(deadline_date) - getdate(today())).days
			
			if days_until in [7, 1]:
				send_tax_deadline_reminder(deadline_name, deadline_date, days_until)
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error checking tax deadlines: {str(e)}", "Tax Deadline Error")


def send_tax_deadline_reminder(deadline_name, deadline_date, days_until):
	"""Send tax deadline reminder to all active clients"""
	try:
		from microsaas.microsaas.services.notification_service import send_notification
		
		# Get all active clients
		clients = frappe.get_all(
			"CA Client",
			filters={"status": "Active"},
			fields=["name", "client_name"]
		)
		
		for client in clients:
			notification_data = {
				"client_name": client.client_name,
				"deadline_name": deadline_name,
				"deadline_date": deadline_date,
				"days_until": days_until
			}
			
			send_notification(
				client=client.name,
				template_type="tax_deadline",
				data=notification_data
			)
		
	except Exception as e:
		frappe.log_error(f"Error sending tax deadline reminder: {str(e)}")


def check_document_expiry():
	"""Check for expiring documents and send reminders"""
	try:
		# Get documents expiring in 30 days
		expiry_date = add_days(today(), 30)
		
		documents = frappe.get_all(
			"CA Document",
			filters={
				"expiry_date": ["<=", expiry_date],
				"expiry_date": [">=", today()]
			},
			fields=["name", "client", "document_name", "expiry_date"]
		)
		
		for doc in documents:
			send_document_expiry_reminder(doc)
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error checking document expiry: {str(e)}", "Document Expiry Error")


def send_document_expiry_reminder(document):
	"""Send document expiry reminder"""
	try:
		from microsaas.microsaas.services.notification_service import send_notification
		
		days_until_expiry = (getdate(document.expiry_date) - getdate(today())).days
		
		notification_data = {
			"client_name": frappe.db.get_value("CA Client", document.client, "client_name"),
			"document_name": document.document_name,
			"expiry_date": document.expiry_date,
			"days_until_expiry": days_until_expiry
		}
		
		send_notification(
			client=document.client,
			template_type="document_expiry",
			data=notification_data
		)
		
	except Exception as e:
		frappe.log_error(f"Error sending document expiry reminder: {str(e)}")


def generate_recurring_invoices():
	"""Generate recurring invoices based on schedule"""
	try:
		# Get all recurring invoices due for generation
		invoices = frappe.get_all(
			"CA Invoice",
			filters={
				"is_recurring": 1,
				"next_generation_date": ["<=", today()],
				"docstatus": 1
			},
			fields=["name", "client", "frequency", "next_generation_date", "end_date"]
		)
		
		for invoice_data in invoices:
			# Check if recurring should continue
			if invoice_data.end_date and getdate(invoice_data.end_date) < getdate(today()):
				continue
			
			# Generate new invoice
			generate_new_invoice(invoice_data.name)
		
		frappe.db.commit()
		
	except Exception as e:
		frappe.log_error(f"Error generating recurring invoices: {str(e)}", "Recurring Invoice Error")


def generate_new_invoice(original_invoice_name):
	"""Generate new invoice from recurring template"""
	try:
		original = frappe.get_doc("CA Invoice", original_invoice_name)
		
		# Create new invoice
		new_invoice = frappe.copy_doc(original)
		new_invoice.invoice_date = today()
		
		# Calculate new due date based on payment terms
		if original.payment_terms == "Net 15":
			new_invoice.due_date = add_days(today(), 15)
		elif original.payment_terms == "Net 30":
			new_invoice.due_date = add_days(today(), 30)
		elif original.payment_terms == "Net 45":
			new_invoice.due_date = add_days(today(), 45)
		elif original.payment_terms == "Net 60":
			new_invoice.due_date = add_days(today(), 60)
		else:
			new_invoice.due_date = today()
		
		new_invoice.status = "Unpaid"
		new_invoice.payment_gateway_reference = None
		new_invoice.portal_link = None
		
		new_invoice.insert(ignore_permissions=True)
		new_invoice.submit()
		
		# Update original invoice's next generation date
		if original.frequency == "Monthly":
			original.next_generation_date = add_months(original.next_generation_date, 1)
		elif original.frequency == "Quarterly":
			original.next_generation_date = add_months(original.next_generation_date, 3)
		elif original.frequency == "Half-Yearly":
			original.next_generation_date = add_months(original.next_generation_date, 6)
		elif original.frequency == "Annual":
			original.next_generation_date = add_months(original.next_generation_date, 12)
		
		original.save(ignore_permissions=True)
		
		frappe.msgprint(f"Generated new invoice {new_invoice.name} from recurring template")
		
	except Exception as e:
		frappe.log_error(f"Error generating new invoice from {original_invoice_name}: {str(e)}")
