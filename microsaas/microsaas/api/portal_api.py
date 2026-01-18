# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

"""
Portal API Endpoints
API methods for client portal functionality
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_client_dashboard(client_name=None):
	"""
	Get dashboard data for client portal
	
	Args:
		client_name: CA Client name (auto-detected from user if not provided)
	
	Returns:
		Dashboard data with invoices, payments, appointments, documents
	"""
	try:
		# Get client from current user if not provided
		if not client_name:
			client_name = frappe.db.get_value("CA Client", {"email": frappe.session.user})
		
		if not client_name:
			frappe.throw(_("No client found for current user"))
		
		client = frappe.get_doc("CA Client", client_name)
		
		# Get recent invoices
		invoices = frappe.get_all(
			"CA Invoice",
			filters={"client": client_name, "docstatus": 1},
			fields=["name", "invoice_date", "due_date", "total_amount", "status"],
			order_by="invoice_date desc",
			limit=5
		)
		
		# Get payment summary
		total_paid = frappe.db.sql("""
			SELECT SUM(amount) as total
			FROM `tabCA Payment`
			WHERE client = %s AND status = 'Completed'
		""", client_name)[0][0] or 0
		
		total_outstanding = frappe.db.sql("""
			SELECT SUM(total_amount) as total
			FROM `tabCA Invoice`
			WHERE client = %s AND status IN ('Unpaid', 'Partially Paid', 'Overdue')
			AND docstatus = 1
		""", client_name)[0][0] or 0
		
		# Get upcoming appointments
		appointments = frappe.get_all(
			"CA Appointment",
			filters={
				"client": client_name,
				"status": "Scheduled",
				"appointment_date": [">=", frappe.utils.today()]
			},
			fields=["name", "appointment_date", "appointment_time", "purpose", "ca_name"],
			order_by="appointment_date asc",
			limit=3
		)
		
		# Get recent documents
		documents = frappe.get_all(
			"CA Document",
			filters={"client": client_name, "client_accessible": 1},
			fields=["name", "document_name", "document_type", "upload_date"],
			order_by="upload_date desc",
			limit=5
		)
		
		return {
			"client": {
				"name": client.client_name,
				"email": client.email,
				"status": client.status
			},
			"summary": {
				"total_paid": total_paid,
				"total_outstanding": total_outstanding,
				"invoice_count": len(invoices),
				"upcoming_appointments": len(appointments)
			},
			"recent_invoices": invoices,
			"upcoming_appointments": appointments,
			"recent_documents": documents
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting client dashboard: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def get_client_invoices(client_name=None, status=None):
	"""Get all invoices for a client"""
	try:
		if not client_name:
			client_name = frappe.db.get_value("CA Client", {"email": frappe.session.user})
		
		filters = {"client": client_name, "docstatus": 1}
		if status:
			filters["status"] = status
		
		invoices = frappe.get_all(
			"CA Invoice",
			filters=filters,
			fields=["name", "invoice_date", "due_date", "total_amount", "status", "portal_link"],
			order_by="invoice_date desc"
		)
		
		return {"invoices": invoices}
		
	except Exception as e:
		frappe.log_error(f"Error getting client invoices: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def get_invoice_details(invoice_name):
	"""Get detailed invoice information"""
	try:
		invoice = frappe.get_doc("CA Invoice", invoice_name)
		
		# Check if user has permission
		client = frappe.db.get_value("CA Client", {"email": frappe.session.user})
		if invoice.client != client:
			frappe.throw(_("Unauthorized access"))
		
		# Get payment history
		payments = frappe.get_all(
			"CA Payment",
			filters={"invoice": invoice_name},
			fields=["name", "amount", "payment_date", "payment_method", "status"],
			order_by="payment_date desc"
		)
		
		return {
			"invoice": {
				"name": invoice.name,
				"client_name": invoice.client_name,
				"invoice_date": invoice.invoice_date,
				"due_date": invoice.due_date,
				"subtotal": invoice.subtotal,
				"tax_rate": invoice.tax_rate,
				"tax_amount": invoice.tax_amount,
				"total_amount": invoice.total_amount,
				"status": invoice.status,
				"portal_link": invoice.portal_link,
				"items": invoice.items
			},
			"payments": payments
		}
		
	except Exception as e:
		frappe.log_error(f"Error getting invoice details: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def get_client_documents(client_name=None):
	"""Get all accessible documents for a client"""
	try:
		if not client_name:
			client_name = frappe.db.get_value("CA Client", {"email": frappe.session.user})
		
		documents = frappe.get_all(
			"CA Document",
			filters={"client": client_name, "client_accessible": 1},
			fields=["name", "document_name", "document_type", "upload_date", "file_size", "file_type"],
			order_by="upload_date desc"
		)
		
		return {"documents": documents}
		
	except Exception as e:
		frappe.log_error(f"Error getting client documents: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def download_document(document_name):
	"""Get download link for a document"""
	try:
		document = frappe.get_doc("CA Document", document_name)
		
		# Check if user has permission
		client = frappe.db.get_value("CA Client", {"email": frappe.session.user})
		if document.client != client or not document.client_accessible:
			frappe.throw(_("Unauthorized access"))
		
		return {
			"download_url": document.download_document()
		}
		
	except Exception as e:
		frappe.log_error(f"Error downloading document: {str(e)}")
		return {"error": str(e)}


@frappe.whitelist()
def upload_client_document(client_name, document_name, document_type, file_url):
	"""Upload a document from client portal"""
	try:
		if not client_name:
			client_name = frappe.db.get_value("CA Client", {"email": frappe.session.user})
		
		# Create document
		doc = frappe.get_doc({
			"doctype": "CA Document",
			"client": client_name,
			"document_name": document_name,
			"document_type": document_type,
			"file_attachment": file_url,
			"visibility": "CA Only",  # Client uploads are CA only by default
			"uploaded_by": frappe.session.user
		})
		doc.insert()
		
		return {
			"success": True,
			"document": doc.name
		}
		
	except Exception as e:
		frappe.log_error(f"Error uploading document: {str(e)}")
		return {"error": str(e)}
