# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
Razorpay Payment Gateway Integration
India-focused payment gateway with UPI, cards, netbanking support
"""

import frappe
from frappe import _
import json
from .base_gateway import BasePaymentGateway


class RazorpayGateway(BasePaymentGateway):
	"""Razorpay payment gateway implementation"""
	
	def __init__(self, settings=None):
		super().__init__(settings)
		self.key_id = self.settings.razorpay_key_id
		self.key_secret = self.settings.get_password("razorpay_key_secret")
		self.webhook_secret = self.settings.get_password("razorpay_webhook_secret")
		
		# Initialize Razorpay client
		try:
			import razorpay
			self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
		except ImportError:
			frappe.throw(_("Razorpay library not installed. Run: pip install razorpay"))
	
	def create_payment_link(self, invoice):
		"""
		Create Razorpay payment link
		
		Args:
			invoice: CA Invoice document
		
		Returns:
			Payment link URL
		"""
		try:
			# Create payment link
			payment_link = self.client.payment_link.create({
				"amount": int(invoice.total_amount * 100),  # Amount in paise
				"currency": invoice.currency,
				"description": f"Invoice {invoice.name}",
				"customer": {
					"name": invoice.client_name,
					"email": invoice.client_email,
					"contact": frappe.db.get_value("CA Client", invoice.client, "phone")
				},
				"notify": {
					"sms": True,
					"email": True
				},
				"reminder_enable": True,
				"notes": {
					"invoice_id": invoice.name,
					"client_id": invoice.client,
					"firm_id": invoice.firm
				},
				"callback_url": f"{frappe.utils.get_url()}/api/method/microsaas.microsaas.integrations.payment_gateway.razorpay_gateway.payment_callback",
				"callback_method": "get"
			})
			
			# Update invoice with payment link
			invoice.payment_gateway_reference = payment_link["id"]
			invoice.portal_link = payment_link["short_url"]
			invoice.save(ignore_permissions=True)
			
			return payment_link["short_url"]
			
		except Exception as e:
			self.log_error(f"Error creating Razorpay payment link: {str(e)}")
			frappe.throw(_("Failed to create payment link"))
	
	def create_payment_intent(self, invoice):
		"""
		Create Razorpay order
		
		Args:
			invoice: CA Invoice document
		
		Returns:
			Order object
		"""
		try:
			order = self.client.order.create({
				"amount": int(invoice.total_amount * 100),  # Amount in paise
				"currency": invoice.currency,
				"receipt": invoice.name,
				"notes": {
					"invoice_id": invoice.name,
					"client_id": invoice.client,
					"firm_id": invoice.firm
				}
			})
			
			return order
			
		except Exception as e:
			self.log_error(f"Error creating Razorpay order: {str(e)}")
			return None
	
	def verify_webhook(self, payload, signature):
		"""
		Verify Razorpay webhook signature
		
		Args:
			payload: Webhook payload (string)
			signature: X-Razorpay-Signature header
		
		Returns:
			Boolean
		"""
		try:
			self.client.utility.verify_webhook_signature(
				payload,
				signature,
				self.webhook_secret
			)
			return True
		except Exception as e:
			self.log_error(f"Webhook signature verification failed: {str(e)}")
			return False
	
	def process_webhook(self, payload):
		"""
		Process Razorpay webhook event
		
		Args:
			payload: Webhook payload dict
		
		Returns:
			Processed event data
		"""
		try:
			event = payload.get("event")
			payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
			
			if event == "payment.captured":
				# Payment successful
				self.handle_payment_success(payment_entity)
			
			elif event == "payment.failed":
				# Payment failed
				self.handle_payment_failure(payment_entity)
			
			return {"status": "processed"}
			
		except Exception as e:
			self.log_error(f"Error processing webhook: {str(e)}")
			return {"status": "error", "message": str(e)}
	
	def handle_payment_success(self, payment_entity):
		"""Handle successful payment"""
		try:
			# Get invoice from notes
			notes = payment_entity.get("notes", {})
			invoice_id = notes.get("invoice_id")
			
			if not invoice_id:
				self.log_error("Invoice ID not found in payment notes")
				return
			
			invoice = frappe.get_doc("CA Invoice", invoice_id)
			
			# Create or update payment record
			payment = frappe.db.exists("CA Payment", {"transaction_id": payment_entity["id"]})
			
			if payment:
				payment_doc = frappe.get_doc("CA Payment", payment)
				payment_doc.status = "Completed"
				payment_doc.gateway_response = json.dumps(payment_entity)
				payment_doc.save(ignore_permissions=True)
			else:
				payment_doc = self.create_payment_record(
					invoice=invoice,
					transaction_id=payment_entity["id"],
					amount=payment_entity["amount"] / 100,  # Convert paise to rupees
					gateway="Razorpay",
					status="Completed"
				)
				payment_doc.gateway_response = json.dumps(payment_entity)
				payment_doc.payment_method = payment_entity.get("method", "").upper()
				payment_doc.save(ignore_permissions=True)
			
			# Submit payment to trigger reconciliation
			if payment_doc.docstatus == 0:
				payment_doc.submit()
			
		except Exception as e:
			self.log_error(f"Error handling payment success: {str(e)}")
	
	def handle_payment_failure(self, payment_entity):
		"""Handle failed payment"""
		try:
			notes = payment_entity.get("notes", {})
			invoice_id = notes.get("invoice_id")
			
			if invoice_id:
				# Create failed payment record
				invoice = frappe.get_doc("CA Invoice", invoice_id)
				payment_doc = self.create_payment_record(
					invoice=invoice,
					transaction_id=payment_entity["id"],
					amount=payment_entity["amount"] / 100,
					gateway="Razorpay",
					status="Failed"
				)
				payment_doc.gateway_response = json.dumps(payment_entity)
				payment_doc.save(ignore_permissions=True)
				
		except Exception as e:
			self.log_error(f"Error handling payment failure: {str(e)}")
	
	def refund_payment(self, payment, amount=None):
		"""
		Refund a Razorpay payment
		
		Args:
			payment: CA Payment document
			amount: Amount to refund in rupees (None for full refund)
		
		Returns:
			Refund object
		"""
		try:
			refund_amount = int((amount or payment.amount) * 100)  # Convert to paise
			
			refund = self.client.payment.refund(
				payment.transaction_id,
				{
					"amount": refund_amount,
					"speed": "normal",
					"notes": {
						"reason": "Customer request"
					}
				}
			)
			
			# Update payment status
			payment.status = "Refunded"
			payment.save(ignore_permissions=True)
			
			return refund
			
		except Exception as e:
			self.log_error(f"Error processing refund: {str(e)}")
			frappe.throw(_("Failed to process refund"))


@frappe.whitelist(allow_guest=True, methods=["POST"])
def webhook():
	"""Razorpay webhook endpoint"""
	try:
		# Get webhook data
		payload = frappe.request.data
		signature = frappe.request.headers.get("X-Razorpay-Signature")
		
		# Parse payload to get firm_id
		payload_dict = json.loads(payload)
		payment_entity = payload_dict.get("payload", {}).get("payment", {}).get("entity", {})
		notes = payment_entity.get("notes", {})
		firm_id = notes.get("firm_id")
		
		# Get settings
		settings = None
		if firm_id:
			settings = frappe.get_doc("CA Firm", firm_id)
		
		if not settings:
			settings = frappe.get_single("CA Settings") # Fallback
			
		# Verify signature
		gateway = RazorpayGateway(settings)
		if not gateway.verify_webhook(payload, signature):
			frappe.throw(_("Invalid webhook signature"))
		
		# Process webhook
		result = gateway.process_webhook(payload_dict)
		
		return result
		
	except Exception as e:
		frappe.log_error(f"Razorpay webhook error: {str(e)}", "Razorpay Webhook Error")
		return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def payment_callback():
	"""Payment callback handler"""
	try:
		# Get payment link ID from query params
		payment_link_id = frappe.form_dict.get("razorpay_payment_link_id")
		payment_id = frappe.form_dict.get("razorpay_payment_id")
		
		if payment_id:
			# Redirect to success page
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = "/payment-success"
		else:
			# Redirect to failure page
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = "/payment-failed"
			
	except Exception as e:
		frappe.log_error(f"Payment callback error: {str(e)}")
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = "/payment-error"


def create_payment_link(invoice):
	"""Helper function to create payment link"""
	gateway = RazorpayGateway()
	return gateway.create_payment_link(invoice)
