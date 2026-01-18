# Sample Notification Templates

This file contains sample notification templates that you can import into your CA MicroSaaS platform.

## How to Use

1. Go to **Notification Template** in Frappe
2. Create new template
3. Copy the content from below
4. Customize as needed

---

## 1. Invoice Sent

**Template Name:** Invoice Sent  
**Template Type:** invoice_sent  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

Your invoice {{invoice_number}} for ₹{{amount}} has been generated.

📅 Due Date: {{due_date}}

You can view and pay your invoice here:
{{portal_link}}

Thank you for your business!

Best regards,
Your CA Team
```

---

## 2. Payment Reminder

**Template Name:** Payment Reminder  
**Template Type:** payment_reminder  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

⏰ Friendly Reminder

Invoice {{invoice_number}} for ₹{{amount}} is due on {{due_date}}.

Please make the payment at your earliest convenience:
{{portal_link}}

Thank you!

Best regards,
Your CA Team
```

---

## 3. Payment Overdue

**Template Name:** Payment Overdue  
**Template Type:** payment_overdue  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

⚠️ Payment Overdue Notice

Invoice {{invoice_number}} for ₹{{amount}} is now {{days_overdue}} days overdue.

Please settle this invoice immediately:
{{portal_link}}

If you have already made the payment, please ignore this message.

For any queries, please contact us.

Best regards,
Your CA Team
```

---

## 4. Payment Received

**Template Name:** Payment Received  
**Template Type:** payment_received  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

✅ Payment Received

We have received your payment of ₹{{amount}} for invoice {{invoice_number}}.

Transaction ID: {{transaction_id}}
Payment Date: {{payment_date}}

Thank you for your prompt payment!

Best regards,
Your CA Team
```

---

## 5. Appointment Reminder

**Template Name:** Appointment Reminder  
**Template Type:** appointment_reminder  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

📅 Appointment Reminder

You have an appointment with {{ca_name}}.

Date: {{appointment_date}}
Time: {{appointment_time}}

Looking forward to meeting you!

Best regards,
Your CA Team
```

---

## 6. Tax Deadline

**Template Name:** Tax Deadline  
**Template Type:** tax_deadline  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

🔔 Important Tax Deadline Reminder

{{deadline_name}} is approaching!

Deadline Date: {{deadline_date}}
Days Remaining: {{days_until}}

Please ensure all required documents are submitted.

Contact us if you need assistance.

Best regards,
Your CA Team
```

---

## 7. Document Expiry

**Template Name:** Document Expiry  
**Template Type:** document_expiry  
**Channel:** WhatsApp  
**Is Active:** Yes

**Template Content:**
```
Dear {{client_name}},

📄 Document Expiry Notice

Your {{document_name}} is expiring soon.

Expiry Date: {{expiry_date}}
Days Remaining: {{days_until_expiry}}

Please renew this document to avoid any compliance issues.

Contact us for assistance with renewal.

Best regards,
Your CA Team
```

---

## Email Templates

You can also create email versions of these templates by:
1. Changing **Channel** to "Email"
2. Using HTML formatting for better presentation
3. Adding your company logo

### Example Email Template (Invoice Sent)

**Template Name:** Invoice Sent Email  
**Template Type:** invoice_sent  
**Channel:** Email  
**Is Active:** Yes

**Template Content:**
```html
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #333;">Invoice Generated</h2>
    
    <p>Dear {{client_name}},</p>
    
    <p>Your invoice <strong>{{invoice_number}}</strong> for <strong>₹{{amount}}</strong> has been generated.</p>
    
    <div style="background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px;">
        <p style="margin: 5px 0;"><strong>Due Date:</strong> {{due_date}}</p>
        <p style="margin: 5px 0;"><strong>Amount:</strong> ₹{{amount}}</p>
    </div>
    
    <p>
        <a href="{{portal_link}}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
            View & Pay Invoice
        </a>
    </p>
    
    <p>Thank you for your business!</p>
    
    <p>Best regards,<br>Your CA Team</p>
</div>
```

---

## Available Variables

Use these variables in your templates:

### Invoice Templates
- `{{client_name}}` - Client name
- `{{invoice_number}}` - Invoice number
- `{{amount}}` - Invoice amount
- `{{due_date}}` - Due date
- `{{portal_link}}` - Payment link
- `{{days_overdue}}` - Days overdue (for overdue template)

### Payment Templates
- `{{client_name}}` - Client name
- `{{invoice_number}}` - Invoice number
- `{{amount}}` - Payment amount
- `{{payment_date}}` - Payment date
- `{{transaction_id}}` - Transaction ID

### Appointment Templates
- `{{client_name}}` - Client name
- `{{appointment_date}}` - Appointment date
- `{{appointment_time}}` - Appointment time
- `{{ca_name}}` - CA name
- `{{hours_before}}` - Hours before appointment

### Tax Deadline Templates
- `{{client_name}}` - Client name
- `{{deadline_name}}` - Deadline name
- `{{deadline_date}}` - Deadline date
- `{{days_until}}` - Days until deadline

### Document Templates
- `{{client_name}}` - Client name
- `{{document_name}}` - Document name
- `{{expiry_date}}` - Expiry date
- `{{days_until_expiry}}` - Days until expiry

---

## Tips for Effective Templates

1. **Keep it concise**: WhatsApp messages should be brief
2. **Use emojis**: Makes messages more engaging (📅 ⏰ ✅ ⚠️ 🔔)
3. **Clear call-to-action**: Include payment links prominently
4. **Professional tone**: Maintain professionalism while being friendly
5. **Test thoroughly**: Send test messages before going live
6. **Personalize**: Use client names and specific details
7. **Timing matters**: Schedule reminders at appropriate times

---

## Customization Ideas

- Add your company logo (for email templates)
- Include office hours and contact information
- Add social media links
- Include tax-saving tips in tax deadline reminders
- Offer early payment discounts in reminders
- Add FAQ links for common questions

---

**Note:** Remember to test all templates before enabling them for production use!
