# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
WhatsApp Notification Service
Integrates with existing whatsapp_saas app to send notifications
"""

import frappe
from frappe import _
import json


def send_notification(client, template_type, data):
	"""
	Send notification to client using specified template
	
	Args:
		client: CA Client document name or object
		template_type: Type of template (invoice_sent, payment_reminder, etc.)
		data: Dictionary of variables for template rendering
	
	Returns:
		Response from whatsapp_saas API
	"""
	try:
		# Get client details
		if isinstance(client, str):
			client_doc = frappe.get_doc("CA Client", client)
		else:
			client_doc = client
			
		# Get Firm Settings
		if not client_doc.firm:
			frappe.log_error(f"Client {client_doc.client_name} is not linked to any CA Firm")
			return None
			
		firm_settings = frappe.get_doc("CA Firm", client_doc.firm)
		
		# Check if WhatsApp notifications are enabled
		if not firm_settings.enable_whatsapp_notifications:
			return None
		
		# Get WhatsApp instance
		if not firm_settings.whatsapp_instance:
			frappe.log_error(f"WhatsApp instance not configured for Firm: {firm_settings.firm_name}")
			return None
		
		# Check if client has WhatsApp number
		if not client_doc.whatsapp_number:
			frappe.log_error(f"Client {client_doc.client_name} does not have WhatsApp number")
			return None
		
		# Get notification template for this Firm
		template = frappe.get_doc("Notification Template", {
			"firm": client_doc.firm,
			"template_type": template_type,
			"channel": "WhatsApp",
			"is_active": 1
		})
		
		if not template:
			frappe.log_error(f"No active WhatsApp template found for type: {template_type} in Firm: {firm_settings.firm_name}")
			return None
		
		# Render template with data
		message = template.render(data)
		
		if not message:
			frappe.log_error("Failed to render notification template")
			return None
		
		# Send via whatsapp_saas
		response = send_whatsapp_message(
			instance_id=firm_settings.whatsapp_instance,
			number=client_doc.whatsapp_number,
			message=message
		)
		
		# Log notification
		log_notification(
			client=client_doc.name,
			template=template.name,
			channel="WhatsApp",
			status="Sent" if response else "Failed",
			message=message,
			response=response
		)
		

		return response
		
	except Exception as e:
		frappe.log_error(f"Error sending WhatsApp notification: {str(e)}", "WhatsApp Notification Error")
		return None

def send_whatsapp_with_file(client, template_type, data, file_url, file_name=None):
	"""
	Send WhatsApp notification with file attachment
	
	Args:
		client: CA Client document name or object
		template_type: Type of template
		data: Dictionary of variables for template rendering
		file_url: Full URL of the file to attach
		file_name: Optional name for the file
	"""
	try:
		# Get client details
		if isinstance(client, str):
			client_doc = frappe.get_doc("CA Client", client)
		else:
			client_doc = client
			
		# Get Firm Settings
		if not client_doc.firm:
			return None
			
		firm_settings = frappe.get_doc("CA Firm", client_doc.firm)
		
		# Check if WhatsApp notifications are enabled
		if not firm_settings.enable_whatsapp_notifications:
			return None
		
		# Get WhatsApp instance
		if not firm_settings.whatsapp_instance:
			return None
		
		# Get notification template for this Firm
		template = frappe.get_doc("Notification Template", {
			"firm": client_doc.firm,
			"template_type": template_type,
			"channel": "WhatsApp",
			"is_active": 1
		})
		
		# Render caption
		caption = ""
		if template:
			caption = template.render(data)
			
		# Prepare payload for whatsapp_saas
		# Assuming whatsapp_saas endpoint supports 'url' or 'media' param for remote files
		args = {
			"instance_id": firm_settings.whatsapp_instance,
			"number": client_doc.whatsapp_number,
			"media": file_url,
			"url": file_url, # sending both to be safe depending on Baileys API expectations
			"caption": caption,
			"type": "document",
			"filename": file_name or "Invoice.pdf",
			"mimetype": "application/pdf"
		}
		
		# Call whatsapp_saas send_media
		# We use frappe.call to invoke the whitelist method, but since we are server-side, 
		# we can import and call if it allows, or use frappe.call which does a local call.
		# However, endpoints.send_media expects frappe.request.files for uploads.
		# If the underlying API supports URL, passing it in kwargs (which becomes data) should work.
		
		from whatsapp_saas.whatsapp_saas.api.endpoints import send_media
		response = send_media(**args)
		
		# Log notification
		log_notification(
			client=client_doc.name,
			template=template.name if template else "Manual File",
			channel="WhatsApp",
			status="Sent" if response else "Failed",
			message=f"File: {file_url}\nCaption: {caption}",
			response=response
		)
		
		return response
		
	except Exception as e:
		frappe.log_error(f"Error sending WhatsApp file: {str(e)}", "WhatsApp File Error")
		return None


def send_whatsapp_message(instance_id, number, message):
	"""
	Send WhatsApp message using whatsapp_saas API
	
	Args:
		instance_id: WhatsApp Instance ID from whatsapp_saas
		number: Recipient WhatsApp number
		message: Message text
	
	Returns:
		API response
	"""
	try:
		# Call whatsapp_saas send_text endpoint
		response = frappe.call(
			"send_text",
			instance_id=instance_id,
			number=number,
			text=message
		)
		
		return response
		
	except Exception as e:
		frappe.log_error(f"Error calling whatsapp_saas API: {str(e)}")
		return None


def log_notification(client, template, channel, status, message, response=None):
	"""
	Log notification delivery
	
	Args:
		client: CA Client name
		template: Notification Template name
		channel: Notification channel (WhatsApp, Email, SMS)
		status: Delivery status
		message: Message content
		response: API response
	"""
	try:
		log = frappe.get_doc({
			"doctype": "Notification Log",
			"client": client,
			"template": template,
			"channel": channel,
			"status": status,
			"message": message,
			"response": json.dumps(response) if response else None
		})
		log.insert(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error logging notification: {str(e)}")


def send_email_notification(client, template_type, data):
	"""
	Send email notification
	
	Args:
		client: CA Client document name or object
		template_type: Type of template
		data: Dictionary of variables for template rendering
	"""
	try:
		# Get client details
		if isinstance(client, str):
			client_doc = frappe.get_doc("CA Client", client)
		else:
			client_doc = client
			
		# Get Firm Settings
		if not client_doc.firm:
			return None
			
		firm_settings = frappe.get_doc("CA Firm", client_doc.firm)
		
		if not firm_settings.enable_email_notifications:
			return None
		
		# Get notification template for this Firm
		template = frappe.get_doc("Notification Template", {
			"firm": client_doc.firm,
			"template_type": template_type,
			"channel": "Email",
			"is_active": 1
		})
		
		if not template:
			return None
		
		# Render template
		message = template.render(data)
		
		# Send email using Frappe's email queue
		frappe.sendmail(
			recipients=[client_doc.email],
			subject=f"Notification: {template_type.replace('_', ' ').title()}",
			message=message,
			delayed=False
		)
		
		# Log notification
		log_notification(
			client=client_doc.name,
			template=template.name,
			channel="Email",
			status="Sent",
			message=message
		)
		
	except Exception as e:
		frappe.log_error(f"Error sending email notification: {str(e)}")
