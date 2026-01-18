# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
Base Payment Gateway Class
Abstract base class for all payment gateway integrations
"""

from abc import ABC, abstractmethod
import frappe


class BasePaymentGateway(ABC):
	"""Abstract base class for payment gateways"""
	
	def __init__(self, settings=None):
		if settings:
			self.settings = settings
		else:
			# Fallback for backward compatibility or when settings are not explicitly passed
			# In multi-tenant mode, this should ideally be avoided
			self.settings = frappe.get_single("CA Settings")
	
	@abstractmethod
	def create_payment_link(self, invoice):
		"""
		Create a payment link for an invoice
		
		Args:
			invoice: CA Invoice document
		
		Returns:
			Payment link URL
		"""
		pass
	
	@abstractmethod
	def create_payment_intent(self, invoice):
		"""
		Create a payment intent/order
		
		Args:
			invoice: CA Invoice document
		
		Returns:
			Payment intent/order object
		"""
		pass
	
	@abstractmethod
	def verify_webhook(self, payload, signature):
		"""
		Verify webhook signature
		
		Args:
			payload: Webhook payload
			signature: Webhook signature
		
		Returns:
			Boolean indicating if signature is valid
		"""
		pass
	
	@abstractmethod
	def process_webhook(self, payload):
		"""
		Process webhook event
		
		Args:
			payload: Webhook payload
		
		Returns:
			Processed event data
		"""
		pass
	
	@abstractmethod
	def refund_payment(self, payment, amount=None):
		"""
		Refund a payment
		
		Args:
			payment: CA Payment document
			amount: Amount to refund (None for full refund)
		
		Returns:
			Refund object
		"""
		pass
	
	def log_error(self, message, title="Payment Gateway Error"):
		"""Log error to Frappe error log"""
		frappe.log_error(message, title)
	
	def create_payment_record(self, invoice, transaction_id, amount, gateway, status="Pending"):
		"""
		Create CA Payment record
		
		Args:
			invoice: CA Invoice document
			transaction_id: Gateway transaction ID
			amount: Payment amount
			gateway: Gateway name
			status: Payment status
		
		Returns:
			CA Payment document
		"""
		try:
			payment = frappe.get_doc({
				"doctype": "CA Payment",
				"invoice": invoice.name,
				"client": invoice.client,
				"firm": invoice.firm,
				"amount": amount,
				"currency": invoice.currency,
				"payment_gateway": gateway,
				"transaction_id": transaction_id,
				"status": status
			})
			payment.insert(ignore_permissions=True)
			return payment
		except Exception as e:
			self.log_error(f"Error creating payment record: {str(e)}")
			return None
