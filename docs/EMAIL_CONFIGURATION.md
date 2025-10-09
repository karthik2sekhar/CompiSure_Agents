# Email Configuration Setup for Commission Statement Auto-Monitor

## 🔧 **Email Setup Required**

Your system is working perfectly but needs email configuration to send reports automatically.

## 📧 **Quick Email Setup**

### **Option 1: Set Environment Variables (Recommended)**

Create a `.env` file or set these environment variables:

```bash
# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=Commission Reconciliation System
EMAIL_RECIPIENTS=recipient1@company.com,recipient2@company.com

# SMTP Settings (Gmail - default)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### **Option 2: PowerShell Environment Variables**

Run these commands in PowerShell (temporary for current session):

```powershell
# Set your Gmail email and app password
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "your-gmail-app-password"
$env:EMAIL_RECIPIENTS = "recipient1@company.com,recipient2@company.com"
$env:SENDER_NAME = "Commission Reconciliation System"
```

### **Option 3: Permanent Windows Environment Variables**

1. Open Windows System Properties → Advanced → Environment Variables
2. Add these User Variables:
   - `SENDER_EMAIL`: your-email@gmail.com
   - `SENDER_PASSWORD`: your-gmail-app-password  
   - `EMAIL_RECIPIENTS`: recipient1@company.com,recipient2@company.com
   - `SENDER_NAME`: Commission Reconciliation System

## 🔑 **Gmail App Password Setup**

**IMPORTANT**: Don't use your regular Gmail password! You need an App Password:

### **Steps to Get Gmail App Password:**
1. Go to your Google Account settings
2. Security → 2-Factor Authentication (must be enabled)
3. App Passwords → Generate App Password
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character password (like: `abcd efgh ijkl mnop`)
6. Use this App Password as `SENDER_PASSWORD`

## ⚡ **Quick Test Setup**

Want to test email right now? Run this in PowerShell:

```powershell
# Replace with your actual email details
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "your-app-password"
$env:EMAIL_RECIPIENTS = "your-email@gmail.com"

# Test email by copying a file to docs folder
copy docs\aetna_commission_statement.pdf docs\test_email_statement.pdf
```

## 📋 **Current System Status**

✅ **File Monitoring**: Working perfectly  
✅ **PDF Processing**: Working with regex patterns  
✅ **Report Generation**: Creating Excel, HTML, PDF, JSON reports  
❌ **Email Distribution**: Needs configuration  

## 🔍 **Troubleshooting**

### **If emails still don't send:**
1. Check Gmail App Password is correct (16 characters, no spaces)
2. Ensure 2-Factor Authentication is enabled on Gmail
3. Verify recipient email addresses are correct
4. Check Windows Firewall/antivirus isn't blocking SMTP

### **Alternative Email Providers:**
```bash
# Office 365
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587

# Yahoo
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587

# Custom SMTP server
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

## 🎯 **Once Configured**

After setting up email configuration, your monitor will automatically:
1. Detect new commission statements
2. Process and reconcile data
3. Generate comprehensive reports
4. **EMAIL reports to stakeholders automatically**

The system will send professional HTML emails with PDF reports attached every time it processes new commission statements!