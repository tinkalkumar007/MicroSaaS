# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
Payment API Endpoints
Whitelisted methods for payment operations
"""

import frappe
from frappe import _


@frappe.whitelist()
def create_payment_link(invoice_name, gateway=None):
	"""
	Create payment link for an invoice
	
	Args:
		invoice_name: CA Invoice name
		gateway: Payment gateway (Razorpay/Stripe) - uses default if not specified
	
	Returns:
		Payment link URL
	"""
	try:
		# Get invoice
		invoice = frappe.get_doc("CA Invoice", invoice_name)
		
		# Check permissions
		if not frappe.has_permission("CA Invoice", "read", invoice):
			frappe.throw(_("Insufficient permissions"))
		
		# Get firm settings
		firm_settings = None
		if invoice.firm:
			firm_settings = frappe.get_doc("CA Firm", invoice.firm)
			
		# Fallback to defaults if no firm or firm settings incomplete
		if not firm_settings:
			firm_settings = frappe.get_single("CA Settings")

		# Get gateway from settings if not specified
		if not gateway:
			gateway = firm_settings.default_payment_gateway
		
		# Create payment link based on gateway
		if gateway == "Razorpay":
			from microsaas.microsaas.integrations.payment_gateway.razorpay_gateway import RazorpayGateway
			gateway_instance = RazorpayGateway(firm_settings)
			payment_link = gateway_instance.create_payment_link(invoice)
		elif gateway == "Stripe":
			from microsaas.microsaas.integrations.payment_gateway.stripe_gateway import StripeGateway
			gateway_instance = StripeGateway(firm_settings)
			payment_link = gateway_instance.create_payment_link(invoice)
		else:
			frappe.throw(_("Unsupported payment gateway: {0}").format(gateway))
		
		return {
			"success": True,
			"payment_link": payment_link,
			"gateway": gateway
		}
		
	except Exception as e:
		frappe.log_error(f"Error creating payment link: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def get_invoice_payment_status(invoice_name):
	"""
	Get payment status for an invoice
	
	Args:
		invoice_name: CA Invoice name
	
	Returns:
		Payment status details
	"""
	try:
		invoice = frappe.get_doc("CA Invoice", invoice_name)
		
		# Get all payments for this invoice
		payments = frappe.get_all(
			"CA Payment",
			filters={"invoice": invoice_name},
			fields=["name", "amount", "status", "payment_date", "payment_gateway", "transaction_id"]
		)
		
		# Calculate total paid
		total_paid = sum([p.amount for p in payments if p.status == "Completed"])
		
		return {
			"invoice_total": invoice.total_amount,
			"total_paid": total_paid,
			"balance": invoice.total_amount - total_paid,
			"status": invoice.status,
			"payments": payments
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting payment status: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def process_manual_payment(invoice_name, amount, payment_method, transaction_id=None, notes=None):
	"""
	Record a manual payment (cash, cheque, bank transfer)
	
	Args:
		invoice_name: CA Invoice name
		amount: Payment amount
		payment_method: Payment method
		transaction_id: Optional transaction reference
		notes: Optional notes
	
	Returns:
		Payment record
	"""
	try:
		invoice = frappe.get_doc("CA Invoice", invoice_name)
		
		# Create payment record
		payment = frappe.get_doc({
			"doctype": "CA Payment",
			"invoice": invoice_name,
			"client": invoice.client,
			"amount": float(amount),
			"currency": invoice.currency,
			"payment_gateway": "Manual",
			"payment_method": payment_method,
			"transaction_id": transaction_id or frappe.generate_hash(length=10),
			"status": "Completed",
			"gateway_response": notes
		})
		
		payment.insert()
		payment.submit()
		
		return {
			"success": True,
			"payment": payment.name
		}
		
	except Exception as e:
		frappe.log_error(f"Error processing manual payment: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def refund_payment(payment_name, amount=None, reason=None):
	"""
	Refund a payment
	
	Args:
		payment_name: CA Payment name
		amount: Amount to refund (None for full refund)
		reason: Refund reason
	
	Returns:
		Refund details
	"""
	try:
		payment = frappe.get_doc("CA Payment", payment_name)
		
		# Check if payment can be refunded
		if payment.status != "Completed":
			frappe.throw(_("Only completed payments can be refunded"))
		
		# Get firm settings
		firm_settings = None
		if payment.firm:
			firm_settings = frappe.get_doc("CA Firm", payment.firm)
			
		# Fallback
		if not firm_settings:
			firm_settings = frappe.get_single("CA Settings")

		# Process refund based on gateway
		if payment.payment_gateway == "Razorpay":
			from microsaas.microsaas.integrations.payment_gateway.razorpay_gateway import RazorpayGateway
			gateway = RazorpayGateway(firm_settings)
			refund = gateway.refund_payment(payment, amount)
		elif payment.payment_gateway == "Stripe":
			from microsaas.microsaas.integrations.payment_gateway.stripe_gateway import StripeGateway
			gateway = StripeGateway(firm_settings)
			refund = gateway.refund_payment(payment, amount)
		elif payment.payment_gateway == "Manual":
			# Manual refund - just update status
			payment.status = "Refunded"
			payment.gateway_response = f"Manual refund: {reason}"
			payment.save()
			refund = {"status": "refunded"}
		else:
			frappe.throw(_("Refund not supported for this payment gateway"))
		
		return {
			"success": True,
			"refund": refund
		}
		
	except Exception as e:
		frappe.log_error(f"Error processing refund: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}
