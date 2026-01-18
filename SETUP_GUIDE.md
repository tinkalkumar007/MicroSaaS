# Quick Setup Guide - CA MicroSaaS Platform

This guide will help you set up the CA MicroSaaS platform in under 30 minutes.

## Step 1: Installation (5 minutes)

```bash
# Install dependencies
cd ~/frappe-bench
bench pip install razorpay stripe

# Migrate database
bench --site [your-site] migrate

# Restart
bench restart
```

## 🚀 Quick Start (Recommended)
Skip manual setup by generating a full test environment with firms, clients, and invoice history:
```bash
bench --site [your-site] execute microsaas.microsaas.setup.demo_data.generate
```
*This creates two firms (Metro CA Services, Global Tax Consultants) and 12 months of report data.*

---

## Manual Setup Guide

## Step 2: Create Your CA Firm (10 minutes)

1. Login to your Frappe site
2. Go to **CA Firm List** -> **New CA Firm**
3. Fill in the following:

### Firm Details
```
Firm Name: Your Firm Name
Address: Your office address
Contact Email: contact@yourfirm.com
Contact Phone: +91XXXXXXXXXX
```

### WhatsApp Integration
```
✓ Enable WhatsApp Notifications
WhatsApp Instance: [Select from whatsapp_saas]
```

### Payment Gateway - Razorpay (Recommended for India)
```
✓ Enable Razorpay
Razorpay Key ID: rzp_test_XXXXX (from Razorpay dashboard)
Razorpay Key Secret: XXXXX (from Razorpay dashboard)
Razorpay Webhook Secret: XXXXX (from Razorpay dashboard)
Default Payment Gateway: Razorpay
```

### Invoice Configuration
```
Invoice Number Series: INV-.#####
Default Tax Rate: 18
Default Payment Terms: Net 30
Default Currency: INR
```

### Notification Preferences
```
✓ Enable Email Notifications
✓ Enable WhatsApp Notifications
✓ Auto Send Invoice
✓ Send Payment Confirmation
```

**Save the Firm**
*Note: Multi-tenancy is built-in. You can create multiple firms if needed.*

## Step 3: Create Notification Templates (10 minutes)

Go to **Notification Template** and create the following templates:

### Template 1: Invoice Sent
```
Template Name: Invoice Sent
Template Type: invoice_sent
Channel: WhatsApp
Is Active: ✓

Template Content:
Dear {{client_name}},

Your invoice {{invoice_number}} for ₹{{amount}} has been generated.

Due Date: {{due_date}}

You can view and pay your invoice here: {{portal_link}}

Thank you for your business!

Best regards,
Your CA Team
```

### Template 2: Payment Reminder
```
Template Name: Payment Reminder
Template Type: payment_reminder
Channel: WhatsApp
Is Active: ✓

Template Content:
Dear {{client_name}},

This is a friendly reminder that invoice {{invoice_number}} for ₹{{amount}} is due on {{due_date}}.

Please make the payment at your earliest convenience: {{portal_link}}

Thank you!
```

### Template 3: Payment Overdue
```
Template Name: Payment Overdue
Template Type: payment_overdue
Channel: WhatsApp
Is Active: ✓

Template Content:
Dear {{client_name}},

Invoice {{invoice_number}} for ₹{{amount}} is now {{days_overdue}} days overdue.

Please settle this invoice immediately: {{portal_link}}

If you have already made the payment, please ignore this message.

Thank you!
```

### Template 4: Payment Received
```
Template Name: Payment Received
Template Type: payment_received
Channel: WhatsApp
Is Active: ✓

Template Content:
Dear {{client_name}},

We have received your payment of ₹{{amount}} for invoice {{invoice_number}}.

Transaction ID: {{transaction_id}}
Payment Date: {{payment_date}}

Thank you for your prompt payment!

Best regards,
Your CA Team
```

### Template 5: Appointment Reminder
```
Template Name: Appointment Reminder
Template Type: appointment_reminder
Channel: WhatsApp
Is Active: ✓

Template Content:
Dear {{client_name}},

This is a reminder for your appointment with {{ca_name}}.

Date: {{appointment_date}}
Time: {{appointment_time}}

Looking forward to meeting you!

Best regards,
Your CA Team
```

### Template 6: Tax Deadline
```
Template Name: Tax Deadline
Template Type: tax_deadline
Channel: WhatsApp
Is Active: ✓

Template Content:
Dear {{client_name}},

Important Reminder: {{deadline_name}} is approaching!

Deadline Date: {{deadline_date}}
Days Remaining: {{days_until}}

Please ensure all required documents are submitted.

Contact us if you need assistance.

Best regards,
Your CA Team
```

## Step 4: Configure Payment Gateway Webhooks (5 minutes)

### Razorpay Webhook Setup

1. Login to Razorpay Dashboard
2. Go to **Settings** → **Webhooks**
3. Click **Create New Webhook**
4. Enter:
   ```
   Webhook URL: https://your-domain.com/api/method/microsaas.razorpay_webhook
   Secret: [Copy from CA Settings]
   Active Events:
   ✓ payment.captured
   ✓ payment.failed
   ```
5. Save

### Stripe Webhook Setup (Optional)

1. Login to Stripe Dashboard
2. Go to **Developers** → **Webhooks**
3. Click **Add endpoint**
4. Enter:
   ```
   Endpoint URL: https://your-domain.com/api/method/microsaas.stripe_webhook
   Events to send:
   ✓ payment_intent.succeeded
   ✓ payment_intent.payment_failed
   ✓ checkout.session.completed
   ```
5. Copy the **Signing secret** to CA Settings
6. Save

## Step 5: Test the System (5 minutes)

### Create a Test Client

```python
# Open Frappe console: bench --site [site] console

import frappe
from frappe.utils import today, add_days

# Create test client
client = frappe.get_doc({
    "doctype": "CA Client",
    "client_name": "Test Client",
    "email": "test@example.com",
    "phone": "+919876543210",
    "whatsapp_number": "+919876543210",
    "company_name": "Test Company Pvt Ltd",
    "business_type": "Private Limited",
    "service_type": "Tax Filing",
    "status": "Active",
    "portal_access_enabled": 1
})
client.insert()
print(f"Created client: {client.name}")
```

### Create a Test Invoice

```python
# Create test invoice
invoice = frappe.get_doc({
    "doctype": "CA Invoice",
    "client": client.name,
    "invoice_date": today(),
    "due_date": add_days(today(), 30),
    "items": [{
        "description": "Tax Filing Services",
        "quantity": 1,
        "rate": 10000,
        "tax_rate": 18
    }],
    "auto_send_on_creation": 1
})
invoice.insert()
invoice.submit()
print(f"Created invoice: {invoice.name}")
print(f"Payment link: {invoice.portal_link}")
```

### Verify

1. Check if WhatsApp notification was sent (check WhatsApp Message Log)
2. Check if payment link was created
3. Try accessing the payment link

## Step 6: Create Your First Real Client

Now you're ready to create real clients!

1. Go to **CA Client** → **New**
2. Fill in client details
3. Enable portal access
4. Save

## Common Issues & Solutions

### WhatsApp notifications not sending
- Check if WhatsApp instance is connected in whatsapp_saas
- Verify WhatsApp instance is selected in CA Settings
- Check WhatsApp Message Log for errors

### Payment link not generating
- Verify payment gateway credentials in CA Settings
- Check if gateway is enabled
- Review error logs

### Scheduler not running
```bash
# Enable scheduler
bench --site [site] enable-scheduler

# Check scheduler status
bench --site [site] doctor
```

### Webhooks not working
- Verify webhook URL is accessible from internet
- Check webhook secret matches
- Review error logs in payment gateway dashboard

## Next Steps

1. **Customize Templates**: Edit notification templates to match your brand voice
2. **Set Up Recurring Invoices**: Create recurring invoices for retainer clients
3. **Configure Tax Deadlines**: Update tax deadlines in `reminder_scheduler.py` for your region
4. **Create More Clients**: Start adding your real clients
5. **Train Your Team**: Show your team how to use the system

## Support

If you encounter issues:
1. Check Frappe error logs: `bench --site [site] logs`
2. Review the README.md for detailed documentation
3. Check the walkthrough.md for architecture details

## Pro Tips

1. **Test Mode First**: Use Razorpay/Stripe test mode before going live
2. **Backup Regularly**: Set up automated backups
3. **Monitor Scheduler**: Check scheduler logs daily initially
4. **Client Feedback**: Ask clients about portal experience
5. **Template Optimization**: A/B test different notification templates

---

**Congratulations!** Your CA MicroSaaS platform is now ready to use! 🎉
