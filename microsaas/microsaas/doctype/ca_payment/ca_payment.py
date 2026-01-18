# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class CAPayment(Document):
	def validate(self):
		"""Validate payment data"""
		# Ensure amount doesn't exceed invoice total
		if self.invoice:
			invoice = frappe.get_doc("CA Invoice", self.invoice)
			if self.amount > invoice.total_amount:
				frappe.throw("Payment amount cannot exceed invoice total")
				
		# Auto-set firm
		if not self.firm:
			if self.invoice:
				self.firm = frappe.db.get_value("CA Invoice", self.invoice, "firm")
			elif self.client:
				self.firm = frappe.db.get_value("CA Client", self.client, "firm")
	
	def on_submit(self):
		"""Actions to perform when payment is completed"""
		if self.status == "Completed":
			self.reconcile_with_invoice()
			self.send_payment_confirmation()
	
	def reconcile_with_invoice(self):
		"""Update invoice payment status"""
		try:
			invoice = frappe.get_doc("CA Invoice", self.invoice)
			
			# Calculate total payments for this invoice
			total_payments = frappe.db.sql("""
				SELECT SUM(amount) as total
				FROM `tabCA Payment`
				WHERE invoice = %s AND status = 'Completed'
			""", self.invoice)[0][0] or 0
			
			# Update invoice status
			if total_payments >= invoice.total_amount:
				invoice.status = "Paid"
			elif total_payments > 0:
				invoice.status = "Partially Paid"
			
			invoice.save(ignore_permissions=True)
			
			# Mark as reconciled
			self.reconciled = 1
			self.reconciliation_date = today()
			self.save()
			
		except Exception as e:
			frappe.log_error(f"Error reconciling payment: {str(e)}")
	
	def send_payment_confirmation(self):
		"""Send payment confirmation notification"""
		try:
			from microsaas.microsaas.services.notification_service import send_notification
			
			notification_data = {
				"client_name": self.client_name,
				"invoice_number": self.invoice,
				"amount": self.amount,
				"payment_date": self.payment_date,
				"transaction_id": self.transaction_id
			}
			
			send_notification(
				client=self.client,
				template_type="payment_received",
				data=notification_data
			)
		except Exception as e:
			frappe.log_error(f"Error sending payment confirmation: {str(e)}")
