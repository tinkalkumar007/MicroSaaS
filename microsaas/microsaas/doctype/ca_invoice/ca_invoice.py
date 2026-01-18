# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, add_months, getdate


class CAInvoice(Document):
	def validate(self):
		"""Validate invoice data before saving"""
		self.calculate_totals()
		self.check_overdue_status()
		
		# Set portal link
		if not self.portal_link:
			self.portal_link = f"/portal/invoice/{self.name}"
			
		# Auto-set firm from client
		if self.client and not self.firm:
			self.firm = frappe.db.get_value("CA Client", self.client, "firm")
	
	def calculate_totals(self):
		"""Calculate subtotal, tax, and total amounts"""
		self.subtotal = 0
		
		for item in self.items:
			# Calculate item amount
			item.amount = item.quantity * item.rate
			self.subtotal += item.amount
		
		# Calculate tax
		self.tax_amount = (self.subtotal * self.tax_rate) / 100
		self.total_amount = self.subtotal + self.tax_amount
	
	def check_overdue_status(self):
		"""Check if invoice is overdue and update status"""
		if self.status == "Unpaid" and getdate(self.due_date) < getdate(today()):
			self.status = "Overdue"
	
	def on_submit(self):
		"""Actions to perform when invoice is submitted"""
		# Send invoice notification if auto-send is enabled
		if self.auto_send_on_creation:
			self.send_invoice_notification()
		
		# Schedule recurring invoice if applicable
		if self.is_recurring and not self.next_generation_date:
			self.schedule_next_invoice()
	
	def send_invoice_notification(self):
		"""Send invoice notification via WhatsApp and Email"""
		try:
			# Import notification service
			from microsaas.microsaas.services.notification_service import send_notification, send_whatsapp_with_file
			
			# Prepare notification data
			notification_data = {
				"client_name": self.client_name,
				"invoice_number": self.name,
				"amount": self.total_amount,
				"due_date": self.due_date,
				"portal_link": self.portal_link
			}
			
			# Generate PDF
			pdf_content = frappe.get_print("CA Invoice", self.name, as_pdf=True)
			
			# Save PDF as File
			file_name = f"Invoice-{self.name}.pdf"
			file_doc = frappe.get_doc({
				"doctype": "File",
				"file_name": file_name,
				"is_private": 0,
				"content": pdf_content,
				"attached_to_doctype": "CA Invoice",
				"attached_to_name": self.name
			})
			file_doc.save(ignore_permissions=True)
			
			# Get full URL (assuming public file)
			file_url = frappe.utils.get_url(file_doc.file_url)
			
			# Send PDF via WhatsApp
			pdf_response = send_whatsapp_with_file(
				client=self.client,
				template_type="invoice_sent",
				data=notification_data,
				file_url=file_url,
				file_name=file_name
			)
			
			if pdf_response:
				frappe.msgprint(f"Invoice PDF sent to {self.client_name} via WhatsApp")
			else:
				# Fallback to text notification if PDF fails or not enabled
				send_notification(
					client=self.client,
					template_type="invoice_sent",
					data=notification_data
				)
				frappe.msgprint(f"Invoice notification sent to {self.client_name}")
				
		except Exception as e:
			frappe.log_error(f"Error sending invoice notification: {str(e)}")
			frappe.msgprint(f"Failed to send notification: {str(e)}")
	
	def schedule_next_invoice(self):
		"""Schedule next recurring invoice generation"""
		if not self.frequency:
			return
		
		# Calculate next generation date based on frequency
		if self.frequency == "Monthly":
			self.next_generation_date = add_months(self.invoice_date, 1)
		elif self.frequency == "Quarterly":
			self.next_generation_date = add_months(self.invoice_date, 3)
		elif self.frequency == "Half-Yearly":
			self.next_generation_date = add_months(self.invoice_date, 6)
		elif self.frequency == "Annual":
			self.next_generation_date = add_months(self.invoice_date, 12)
		
		self.save()
	
	def create_payment_link(self, gateway=None):
		"""Create payment link for the invoice"""
		try:
			# Get firm settings
			firm_settings = None
			if self.firm:
				firm_settings = frappe.get_doc("CA Firm", self.firm)
				
			if not firm_settings:
				firm_settings = frappe.get_single("CA Settings") # Fallback
			
			# Get gateway from settings if not specified
			if not gateway:
				gateway = firm_settings.default_payment_gateway
			
			# Import and use appropriate gateway
			if gateway == "Razorpay":
				from microsaas.microsaas.integrations.payment_gateway.razorpay_gateway import RazorpayGateway
				gateway_instance = RazorpayGateway(firm_settings)
				payment_link = gateway_instance.create_payment_link(self)
			elif gateway == "Stripe":
				from microsaas.microsaas.integrations.payment_gateway.stripe_gateway import StripeGateway
				gateway_instance = StripeGateway(firm_settings)
				payment_link = gateway_instance.create_payment_link(self)
			else:
				frappe.throw(f"Unsupported payment gateway: {gateway}")
			
			# Return just the link string as before, or dict? Original returned create_payment_link(self) which returned URL string.
			return payment_link
			
		except Exception as e:
			frappe.log_error(f"Error creating payment link: {str(e)}")
			frappe.throw(f"Failed to create payment link: {str(e)}")
