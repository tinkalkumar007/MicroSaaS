# CA MicroSaaS Platform

A comprehensive Frappe-based platform for Chartered Accountants to manage clients, invoicing, payments, and automated communications.

## Features

### 📋 Client Management
- Complete client profiles with business details
- Service type tracking and categorization
- Priority-based client management
- Automatic portal user creation
- WhatsApp integration for each client

### 💰 Invoicing & Billing
- Professional invoice generation with line items
- Recurring billing (Monthly, Quarterly, Half-Yearly, Annual)
- Multi-currency support
- Automatic tax calculations
- Payment link generation
- Overdue tracking and status management

### 💳 Payment Processing
- **Razorpay Integration** (India-focused)
  - UPI, Cards, Net Banking, Wallets
  - Automatic payment link generation
  - Webhook-based payment confirmation
- **Stripe Integration** (International)
  - Card payments
  - Payment intents and checkout sessions
  - Webhook handling
- Manual payment recording (Cash, Cheque, Bank Transfer)
- Automated payment reconciliation
- Refund processing

### 📱 WhatsApp Notifications
- Integration with existing `whatsapp_saas` app
- Template-based messaging with Jinja2
- Automatic notifications for:
  - Invoice sent
  - Payment reminders
  - Payment received
  - Appointment reminders
  - Tax deadlines
  - Document expiry

### 🤖 Automation
- **Invoice Reminders**: 3 days before, on due date, overdue escalation
- **Appointment Reminders**: 24 hours and 1 hour before
- **Tax Deadline Alerts**: Pre-configured Indian tax calendar
- **Document Expiry Tracking**: 30-day advance notice
- **Recurring Invoice Generation**: Automatic daily generation at 9 AM

### 📅 Appointment Management
- Schedule client meetings
- Video call, phone call, or in-person options
- Automatic reminders
- Status tracking (Scheduled, Completed, Cancelled)

### 📄 Document Management
- Secure document storage
- Version control
- Access control (CA only or client accessible)
- Compliance tracking with expiry dates
- Digital signature support
- File metadata tracking

### 🌐 Client Portal
- Dashboard with account summary
- Invoice viewing and payment
- Payment history
- Document access and upload
- Appointment scheduling

## Installation

### Prerequisites
- Frappe Framework (v14 or higher)
- Python 3.8+
- `whatsapp_saas` app installed

### Steps

1. **Install on site**
   ```bash
   bench --site [your-site] install-app microsaas
   ```

2. **Install dependencies**
   ```bash
   bench pip install razorpay stripe
   ```

3. **Migrate database**
   ```bash
   bench --site [your-site] migrate
   ```

4. **Restart bench**
   ```bash
   bench restart
   ```

## Configuration

### 1. CA Settings

Navigate to **CA Settings** in your Frappe site and configure:

#### Company Information
- CA Firm Name
- Address
- Contact Email & Phone
- Logo

#### WhatsApp Integration
- Select WhatsApp Instance from `whatsapp_saas` app
- Enable WhatsApp notifications

#### Payment Gateways

**Razorpay:**
- Enable Razorpay
- Enter Key ID
- Enter Key Secret
- Enter Webhook Secret

**Stripe:**
- Enable Stripe
- Enter API Key
- Enter Webhook Secret

#### Invoice Configuration
- Invoice number series
- Default tax rate (GST: 18%)
- Default payment terms
- Default currency (INR)

### 2. Notification Templates

Create templates for each notification type:

**Template Types:**
- `invoice_sent`
- `payment_reminder`
- `payment_overdue`
- `payment_received`
- `appointment_reminder`
- `tax_deadline`
- `document_expiry`

**Example Template (invoice_sent):**
```
Dear {{client_name}},

Your invoice {{invoice_number}} for ₹{{amount}} has been generated.

Due Date: {{due_date}}

You can view and pay your invoice here: {{portal_link}}

Thank you for your business!
```

### 3. Payment Gateway Webhooks

**Razorpay:**
- URL: `https://your-domain.com/api/method/microsaas.razorpay_webhook`
- Events: `payment.captured`, `payment.failed`
- Secret: Copy from CA Settings

**Stripe:**
- URL: `https://your-domain.com/api/method/microsaas.stripe_webhook`
- Events: `payment_intent.succeeded`, `payment_intent.payment_failed`, `checkout.session.completed`
- Secret: Copy from CA Settings

## Usage

### Creating a Client

```python
client = frappe.get_doc({
    "doctype": "CA Client",
    "client_name": "ABC Pvt Ltd",
    "email": "contact@abc.com",
    "phone": "+919876543210",
    "whatsapp_number": "+919876543210",
    "company_name": "ABC Private Limited",
    "gst_number": "27AABCU9603R1ZM",
    "business_type": "Private Limited",
    "service_type": "Tax Filing",
    "portal_access_enabled": 1
})
client.insert()
```

### Creating an Invoice

```python
invoice = frappe.get_doc({
    "doctype": "CA Invoice",
    "client": "CLI-00001",
    "invoice_date": today(),
    "due_date": add_days(today(), 30),
    "items": [{
        "description": "Annual Tax Filing Services",
        "quantity": 1,
        "rate": 25000,
        "tax_rate": 18
    }],
    "auto_send_on_creation": 1
})
invoice.insert()
invoice.submit()  # Auto-sends notification and creates payment link
```

### Setting Up Recurring Invoice

```python
invoice.is_recurring = 1
invoice.frequency = "Monthly"
invoice.next_generation_date = add_months(today(), 1)
invoice.save()
```

### Recording Manual Payment

```python
frappe.call({
    "method": "microsaas.process_manual_payment",
    "args": {
        "invoice_name": "INV-00001",
        "amount": 25000,
        "payment_method": "Bank Transfer",
        "transaction_id": "TXN123456"
    }
})
```

## API Endpoints

### Payment API
- `microsaas.create_payment_link` - Generate payment link
- `microsaas.get_invoice_payment_status` - Check payment status
- `microsaas.process_manual_payment` - Record manual payment
- `microsaas.refund_payment` - Process refund

### Portal API
- `get_client_dashboard` - Dashboard data
- `get_client_invoices` - Invoice list
- `get_invoice_details` - Invoice details
- `get_client_documents` - Document list
- `download_document` - Download document
- `upload_client_document` - Upload document

## Scheduled Jobs

The following jobs run automatically:

- **Daily (All)**: Invoice reminders, tax deadline checks, document expiry checks
- **Hourly**: Appointment reminders
- **Daily at 9 AM**: Recurring invoice generation

## DocTypes

### Core DocTypes
- **CA Client** - Client management
- **CA Invoice** - Invoice generation
- **CA Invoice Item** - Invoice line items (child table)
- **CA Payment** - Payment tracking
- **CA Appointment** - Appointment scheduling
- **CA Document** - Document management
- **CA Settings** - Global configuration (Single)
- **Notification Template** - Message templates

## Architecture

```
microsaas/
├── microsaas/
│   ├── doctype/          # All DocTypes
│   ├── services/         # Business logic services
│   │   ├── notification_service.py
│   │   └── reminder_scheduler.py
│   ├── integrations/     # External integrations
│   │   └── payment_gateway/
│   │       ├── base_gateway.py
│   │       ├── razorpay_gateway.py
│   │       └── stripe_gateway.py
│   └── api/              # API endpoints
│       ├── payment_api.py
│       └── portal_api.py
```

## Security

- Role-based access control (CA Admin, CA User, Client, Accountant)
- Client data isolation
- Secure payment processing (PCI DSS compliant gateways)
- Document access control
- API authentication via Frappe sessions

## Support

For issues and feature requests, please create an issue on GitHub.

## License

MIT License

## Credits

Developed by India100x Pvt. Ltd.