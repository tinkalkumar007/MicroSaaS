# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
Stripe Payment Gateway Integration
International payment gateway with card payments and subscriptions
"""

import frappe
from frappe import _
import json
from .base_gateway import BasePaymentGateway


class StripeGateway(BasePaymentGateway):
	"""Stripe payment gateway implementation"""
	
	def __init__(self, settings=None):
		super().__init__(settings)
		self.api_key = self.settings.get_password("stripe_api_key")
		self.webhook_secret = self.settings.get_password("stripe_webhook_secret")
		
		# Initialize Stripe
		try:
			import stripe
			stripe.api_key = self.api_key
			self.stripe = stripe
		except ImportError:
			frappe.throw(_("Stripe library not installed. Run: pip install stripe"))
	
	def create_payment_link(self, invoice):
		"""
		Create Stripe payment link
		
		Args:
			invoice: CA Invoice document
		
		Returns:
			Payment link URL
		"""
		try:
			# Create payment link
			payment_link = self.stripe.PaymentLink.create(
				line_items=[{
					"price_data": {
						"currency": invoice.currency.lower(),
						"product_data": {
							"name": f"Invoice {invoice.name}",
							"description": f"Payment for {invoice.client_name}"
						},
						"unit_amount": int(invoice.total_amount * 100)  # Amount in cents
					},
					"quantity": 1
				}],
				metadata={
					"invoice_id": invoice.name,
					"client_id": invoice.client,
					"firm_id": invoice.firm
				},
				after_completion={
					"type": "redirect",
					"redirect": {
						"url": f"{frappe.utils.get_url()}/payment-success?invoice={invoice.name}"
					}
				}
			)
			
			# Update invoice
			invoice.payment_gateway_reference = payment_link.id
			invoice.portal_link = payment_link.url
			invoice.save(ignore_permissions=True)
			
			return payment_link.url
			
		except Exception as e:
			self.log_error(f"Error creating Stripe payment link: {str(e)}")
			frappe.throw(_("Failed to create payment link"))
	
	def create_payment_intent(self, invoice):
		"""
		Create Stripe payment intent
		
		Args:
			invoice: CA Invoice document
		
		Returns:
			Payment intent object
		"""
		try:
			intent = self.stripe.PaymentIntent.create(
				amount=int(invoice.total_amount * 100),  # Amount in cents
				currency=invoice.currency.lower(),
				metadata={
					"invoice_id": invoice.name,
					"client_id": invoice.client,
					"firm_id": invoice.firm
				},
				description=f"Invoice {invoice.name}"
			)
			
			return intent
			
		except Exception as e:
			self.log_error(f"Error creating Stripe payment intent: {str(e)}")
			return None
	
	def verify_webhook(self, payload, signature):
		"""
		Verify Stripe webhook signature
		
		Args:
			payload: Webhook payload (bytes)
			signature: Stripe-Signature header
		
		Returns:
			Event object or None
		"""
		try:
			event = self.stripe.Webhook.construct_event(
				payload,
				signature,
				self.webhook_secret
			)
			return event
		except Exception as e:
			self.log_error(f"Webhook signature verification failed: {str(e)}")
			return None
	
	def process_webhook(self, event):
		"""
		Process Stripe webhook event
		
		Args:
			event: Stripe event object
		
		Returns:
			Processed event data
		"""
		try:
			event_type = event["type"]
			
			if event_type == "payment_intent.succeeded":
				self.handle_payment_success(event["data"]["object"])
			
			elif event_type == "payment_intent.payment_failed":
				self.handle_payment_failure(event["data"]["object"])
			
			elif event_type == "checkout.session.completed":
				self.handle_checkout_completed(event["data"]["object"])
			
			return {"status": "processed"}
			
		except Exception as e:
			self.log_error(f"Error processing webhook: {str(e)}")
			return {"status": "error", "message": str(e)}
	
	def handle_payment_success(self, payment_intent):
		"""Handle successful payment intent"""
		try:
			metadata = payment_intent.get("metadata", {})
			invoice_id = metadata.get("invoice_id")
			
			if not invoice_id:
				self.log_error("Invoice ID not found in payment intent metadata")
				return
			
			invoice = frappe.get_doc("CA Invoice", invoice_id)
			
			# Create or update payment record
			payment = frappe.db.exists("CA Payment", {"transaction_id": payment_intent["id"]})
			
			if payment:
				payment_doc = frappe.get_doc("CA Payment", payment)
				payment_doc.status = "Completed"
				payment_doc.gateway_response = json.dumps(payment_intent)
				payment_doc.save(ignore_permissions=True)
			else:
				payment_doc = self.create_payment_record(
					invoice=invoice,
					transaction_id=payment_intent["id"],
					amount=payment_intent["amount"] / 100,  # Convert cents to dollars
					gateway="Stripe",
					status="Completed"
				)
				payment_doc.gateway_response = json.dumps(payment_intent)
				payment_doc.payment_method = payment_intent.get("payment_method_types", ["card"])[0].upper()
				payment_doc.save(ignore_permissions=True)
			
			# Submit payment
			if payment_doc.docstatus == 0:
				payment_doc.submit()
			
		except Exception as e:
			self.log_error(f"Error handling payment success: {str(e)}")
	
	def handle_payment_failure(self, payment_intent):
		"""Handle failed payment intent"""
		try:
			metadata = payment_intent.get("metadata", {})
			invoice_id = metadata.get("invoice_id")
			
			if invoice_id:
				invoice = frappe.get_doc("CA Invoice", invoice_id)
				payment_doc = self.create_payment_record(
					invoice=invoice,
					transaction_id=payment_intent["id"],
					amount=payment_intent["amount"] / 100,
					gateway="Stripe",
					status="Failed"
				)
				payment_doc.gateway_response = json.dumps(payment_intent)
				payment_doc.save(ignore_permissions=True)
				
		except Exception as e:
			self.log_error(f"Error handling payment failure: {str(e)}")
	
	def handle_checkout_completed(self, session):
		"""Handle completed checkout session"""
		try:
			metadata = session.get("metadata", {})
			invoice_id = metadata.get("invoice_id")
			
			if invoice_id:
				# Retrieve payment intent
				payment_intent_id = session.get("payment_intent")
				if payment_intent_id:
					payment_intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
					self.handle_payment_success(payment_intent)
					
		except Exception as e:
			self.log_error(f"Error handling checkout completion: {str(e)}")
	
	def refund_payment(self, payment, amount=None):
		"""
		Refund a Stripe payment
		
		Args:
			payment: CA Payment document
			amount: Amount to refund (None for full refund)
		
		Returns:
			Refund object
		"""
		try:
			refund_amount = int((amount or payment.amount) * 100)  # Convert to cents
			
			refund = self.stripe.Refund.create(
				payment_intent=payment.transaction_id,
				amount=refund_amount
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
	"""Stripe webhook endpoint"""
	try:
		payload = frappe.request.data
		signature = frappe.request.headers.get("Stripe-Signature")
		
		# Parse payload to get firm_id
		try:
			data = json.loads(payload)
			firm_id = data.get("data", {}).get("object", {}).get("metadata", {}).get("firm_id")
		except:
			firm_id = None
			
		# Get settings
		settings = None
		if firm_id:
			settings = frappe.get_doc("CA Firm", firm_id)
			
		if not settings:
			settings = frappe.get_single("CA Settings") # Fallback
		
		gateway = StripeGateway(settings)
		event = gateway.verify_webhook(payload, signature)
		
		if not event:
			frappe.throw(_("Invalid webhook signature"))
		
		result = gateway.process_webhook(event)
		return result
		
	except Exception as e:
		frappe.log_error(f"Stripe webhook error: {str(e)}", "Stripe Webhook Error")
		return {"status": "error", "message": str(e)}


def create_payment_link(invoice):
	"""Helper function to create payment link"""
	gateway = StripeGateway()
	return gateway.create_payment_link(invoice)
