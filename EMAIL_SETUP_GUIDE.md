# 📧 Email Setup Instructions
## **Commission Reconciliation System - Email Integration**

---

## 🎯 **Quick Setup (5 minutes)**

### **Step 1: Configure Email Settings**

Set up your email configuration using environment variables (recommended for security):

```powershell
# Gmail Configuration (most common)
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "your-app-password"  # See Gmail setup below
$env:SENDER_NAME = "Commission Reconciliation System"
$env:EMAIL_RECIPIENTS = "owner@agency.com,accounting@agency.com,manager@agency.com"
```

### **Step 2: Gmail Setup (If using Gmail)**

1. **Enable 2-Factor Authentication**:
   - Go to Google Account Settings → Security
   - Enable 2-Step Verification

2. **Create App Password**:
   - Go to Google Account Settings → Security → 2-Step Verification
   - Click "App passwords"
   - Select "Mail" and your device
   - Copy the generated 16-character password
   - Use this password in `SENDER_PASSWORD` (not your regular Gmail password)

### **Step 3: Test Email Configuration**

```python
# Test email functionality
from src.email_service import EmailService

email_service = EmailService()
success = email_service.send_test_email("your-test@email.com")
print(f"Test email result: {success}")
```

---

## 🔧 **Configuration Options**

### **Environment Variables (Recommended)**

```powershell
# Required Settings
$env:SMTP_SERVER = "smtp.gmail.com"           # SMTP server
$env:SMTP_PORT = "587"                        # SMTP port  
$env:SENDER_EMAIL = "system@agency.com"       # Sender email
$env:SENDER_PASSWORD = "app-password"         # Email password/token
$env:EMAIL_RECIPIENTS = "user1@domain.com,user2@domain.com"  # Recipients

# Optional Settings
$env:SENDER_NAME = "Commission System"        # Display name
```

### **Common SMTP Settings**

| Provider | SMTP Server | Port | Security |
|----------|-------------|------|----------|
| **Gmail** | smtp.gmail.com | 587 | TLS |
| **Outlook/Hotmail** | smtp-mail.outlook.com | 587 | TLS |
| **Yahoo** | smtp.mail.yahoo.com | 587 | TLS |
| **Custom** | your-server.com | 587/465 | TLS/SSL |

---

## 📧 **Email Features**

### **Automatic PDF Attachment**
- PDF reconciliation report automatically attached
- Complete commission analysis included
- Professional formatting and branding

### **HTML Email Body**
- Executive summary with key metrics
- Carrier breakdown table
- Visual status indicators
- Professional styling

### **Email Content Includes**:
- 📊 **Total commissions processed**
- 🏢 **Number of carriers analyzed**  
- ⚠️ **Total discrepancies found**
- 📋 **Carrier-by-carrier breakdown**
- 📎 **Detailed PDF report attachment**

---

## 🚀 **Usage Examples**

### **1. Basic Email Sending**
```python
# After running reconciliation
from src.email_service import EmailService

email_service = EmailService()
success = email_service.send_reconciliation_report(
    pdf_path="reports/commission_report.pdf",
    recipients=["manager@agency.com", "accounting@agency.com"],
    reconciliation_results=results
)
```

### **2. Custom SMTP Configuration**
```python
smtp_config = {
    'smtp_server': 'smtp.office365.com',
    'smtp_port': 587,
    'sender_email': 'reports@agency.com',
    'sender_password': 'your-password',
    'sender_name': 'Agency Commission System'
}

email_service.send_reconciliation_report(
    pdf_path="report.pdf",
    recipients=["owner@agency.com"],
    reconciliation_results=results,
    smtp_config=smtp_config
)
```

### **3. Test Email Configuration**
```python
# Send test email to verify setup
email_service = EmailService()
success = email_service.send_test_email("test@email.com")
print(f"Email test {'passed' if success else 'failed'}")
```

---

## ⚙️ **Integration with Main System**

The email functionality is now integrated with the main reconciliation process:

```bash
# Set recipients and run system
$env:EMAIL_RECIPIENTS = "owner@agency.com,accounting@agency.com"
python main.py

# System will automatically:
# 1. Process commissions
# 2. Generate reports  
# 3. Send PDF report via email
# 4. Log email status
```

---

## 🛡️ **Security Best Practices**

### **1. Use Environment Variables**
- Never hardcode passwords in code
- Use environment variables for sensitive data
- Consider using `.env` files for local development

### **2. App Passwords**
- Use App Passwords for Gmail (not regular password)
- Generate unique passwords for different applications
- Revoke unused App Passwords regularly

### **3. SMTP Security**
- Always use TLS/SSL encryption (port 587 with TLS)
- Avoid port 25 (unencrypted)
- Use authenticated SMTP servers

---

## 🔍 **Troubleshooting**

### **Common Issues**

| Issue | Solution |
|-------|----------|
| **"Authentication failed"** | Use App Password for Gmail, check credentials |
| **"Connection refused"** | Verify SMTP server and port settings |
| **"Recipients not specified"** | Set EMAIL_RECIPIENTS environment variable |
| **"PDF not found"** | Ensure reports are generated before sending |

### **Testing Steps**

1. **Test SMTP Connection**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email', 'your-app-password')
   server.quit()
   print("SMTP connection successful!")
   ```

2. **Test Email Service**:
   ```python
   from src.email_service import EmailService
   service = EmailService()
   result = service.send_test_email("test@domain.com")
   ```

3. **Check Environment Variables**:
   ```powershell
   echo $env:SENDER_EMAIL
   echo $env:EMAIL_RECIPIENTS
   ```

---

## 📋 **Complete Setup Checklist**

### **Before First Use**
- [ ] Set SMTP server configuration
- [ ] Set sender email credentials  
- [ ] Set recipient email addresses
- [ ] Test email configuration
- [ ] Verify PDF reports are generated

### **For Gmail Users**
- [ ] Enable 2-Factor Authentication
- [ ] Generate App Password
- [ ] Use App Password (not regular password)
- [ ] Test with Gmail settings

### **For Production Use**
- [ ] Use secure credentials storage
- [ ] Set up monitoring/logging
- [ ] Configure backup recipients
- [ ] Test failover scenarios

---

## ✅ **Ready to Use**

Once configured, the system will automatically send PDF reports via email after each reconciliation run:

```bash
# Run reconciliation with email
python main.py

# Output will include:
# ✅ Commission reconciliation completed successfully!
# ✅ Email report sent successfully to: owner@agency.com, accounting@agency.com
# ✅ Reports generated: [list of files]
```

**Your commission reconciliation reports will now be automatically delivered to stakeholders via email!** 📧🚀