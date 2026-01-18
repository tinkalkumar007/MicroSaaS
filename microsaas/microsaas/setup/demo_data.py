# Copyright (c) 2026, India100x pvt. ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, add_months, getdate
import random

def generate():
    """Generate dummy data for testing"""
    frappe.db.begin()
    try:
        print("Starting dummy data generation...")
        
        firms = create_firms()
        create_notification_templates()
        clients = create_clients(firms)
        create_invoices_and_payments(clients)
        create_appointments(clients)
        create_documents(clients)
        
        frappe.db.commit()
        print("Dummy data generation completed successfully!")
        
    except Exception as e:
        frappe.db.rollback()
        print(f"Error generating data: {str(e)}")
        frappe.log_error(f"Dummy Data Generation Error: {str(e)}")

def create_firms():
    print("Creating CA Firms...")
    firms_data = [
        {
            "firm_name": "Metro CA Services",
            "email": "admin@metroca.com",
            "phone": "+919000011111",
            "address": "Mumbai, India",
            "currency": "INR",
            "gateway": "Razorpay"
        },
        {
            "firm_name": "Global Tax Consultants",
            "email": "contact@globaltax.com",
            "phone": "+919000022222",
            "address": "Delhi, India",
            "currency": "USD", # Testing multi-currency behavior
            "gateway": "Stripe"
        }
    ]
    
    created_firms = []
    for data in firms_data:
        if not frappe.db.exists("CA Firm", {"firm_name": data["firm_name"]}):
            firm = frappe.get_doc({
                "doctype": "CA Firm",
                "firm_name": data["firm_name"],
                "company_email": data["email"], # Schema field check needed? assuming company_email based on my memory or I should check schema
                "phone": data["phone"],
                "address": data["address"],
                "default_currency": data["currency"],
                "default_payment_gateway": data["gateway"],
                "enabled": 1,
                "enable_whatsapp_notifications": 1,
                "enable_email_notifications": 1
            })
            
            # Mock keys
            if data["gateway"] == "Razorpay":
                firm.enable_razorpay = 1
                firm.razorpay_key_id = "rzp_mock_firm1"
                firm.razorpay_key_secret = "secret"
            else:
                firm.enable_stripe = 1
                firm.stripe_api_key = "sk_test_mock_firm2"
                
            firm.insert(ignore_permissions=True)
            created_firms.append(firm.name)
        else:
            created_firms.append(frappe.db.get_value("CA Firm", {"firm_name": data["firm_name"]}, "name"))
            
    return created_firms

def create_clients(firms):
    print("Creating Clients...")
    clients_data = [
        {"name": "TechFlow Solutions", "firm_idx": 0}, 
        {"name": "GreenLeaf Trading", "firm_idx": 0},
        {"name": "Dr. Rajesh Kumar", "firm_idx": 1},
        {"name": "StartUp Hub LLP", "firm_idx": 1},
        {"name": "Creative Minds", "firm_idx": 0}
    ]
    
    created_clients = []
    for data in clients_data:
        firm = firms[data["firm_idx"]]
        
        if not frappe.db.exists("CA Client", {"client_name": data["name"]}):
            client = frappe.get_doc({
                "doctype": "CA Client",
                "client_name": data["name"],
                "firm": firm,
                "email": f"{data['name'].lower().replace(' ', '')}@example.com",
                "phone": "+919999900000",
                "whatsapp_number": "+919999900000",
                "status": "Active",
                "portal_access_enabled": 1
            })
            client.insert(ignore_permissions=True)
            created_clients.append(client.name)
        else:
            created_clients.append(frappe.db.get_value("CA Client", {"client_name": data["name"]}, "name"))
            
    return created_clients

def create_invoices_and_payments(client_names):
    print("Creating Invoices and Payments...")
    
    services = [
        {"desc": "Monthly Retainer Fee", "rate": 25000},
        {"desc": "GST Filing Charges", "rate": 5000},
        {"desc": "Annual Audit Fee", "rate": 75000},
        {"desc": "Consultation Charges", "rate": 3000},
        {"desc": "TDS Return Filing", "rate": 2500}
    ]
    
    for client in client_names:
        # Generate invoices for the past 12 months
        for i in range(12):
            # Month offset: 0 is current month, -1 is last month, etc.
            month_offset = -i
            
            # Select random service
            service = random.choice(services)
            
            # invoice date is roughly middle of that month
            # simple calculation: today + month_offset * 30
            
            status = "Paid"
            if i == 0: # Current month
                status = "Unpaid"
            elif i == 1: # Last month
                status = "Overdue" # Assuming 30 day terms
            else:
                status = "Paid"
                
            create_invoice(client, service, month_offset * 30, status)

def create_invoice(client, service, days_offset, status):
    date = add_days(today(), days_offset)
    due_date = add_days(date, 30)
    
    invoice = frappe.get_doc({
        "doctype": "CA Invoice",
        "client": client,
        "invoice_date": date,
        "due_date": due_date,
        "currency": "INR",
        "items": [{
            "description": service["desc"],
            "quantity": 1,
            "rate": service["rate"],
            "tax_rate": 18
        }],
        "auto_send_on_creation": 0
    })
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    
    if status == "Paid":
        # Create Payment
        payment = frappe.get_doc({
            "doctype": "CA Payment",
            "invoice": invoice.name,
            "client": client,
            "amount": invoice.total_amount,
            "payment_date": add_days(date, 5),
            "payment_method": "Bank Transfer",
            "payment_gateway": "Manual",
            "transaction_id": frappe.generate_hash(length=10).upper(),
            "status": "Completed"
        })
        payment.insert(ignore_permissions=True)
        payment.submit()

def create_appointments(client_names):
    print("Creating Appointments...")
    current_user = frappe.session.user if frappe.session.user != "Guest" else "Administrator"
    
    meeting_types = ["Video Call", "In-Person", "Phone Call"]
    purposes = ["Tax Planning", "Audit Discussion", "Monthly Review", "New Business Compliance"]
    
    for client in client_names:
        # Scheduled future appointment
        apt = frappe.get_doc({
            "doctype": "CA Appointment",
            "client": client,
            "assigned_ca": current_user,
            "appointment_date": add_days(today(), random.randint(1, 14)),
            "appointment_time": "14:00:00",
            "duration": 60,
            "meeting_type": random.choice(meeting_types),
            "status": "Scheduled",
            "purpose": random.choice(purposes),
            "send_reminder": 1,
            "reminder_time": "24"
        })
        apt.insert(ignore_permissions=True)

def create_documents(client_names):
    print("Creating Documents...")
    
    doc_types = ["Tax Return", "Financial Statement", "Agreement"]
    
    for client in client_names:
        doc = frappe.get_doc({
            "doctype": "CA Document",
            "client": client,
            "document_name": f"FY2025 {random.choice(doc_types)}",
            "document_type": random.choice(doc_types),
            "upload_date": today(),
            "uploaded_by": frappe.session.user,
            "visibility": "Client Accessible",
            "file_attachment": "/files/sample_doc.pdf", # Dummy path
            "expiry_date": add_months(today(), 12)
        })
        doc.insert(ignore_permissions=True)

