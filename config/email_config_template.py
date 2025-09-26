# Email Configuration for Commission Reconciliation System
# Copy this file to config/email_config.py and fill in your email settings

# SMTP Server Configuration
# For Gmail: smtp.gmail.com, port 587
# For Outlook: smtp-mail.outlook.com, port 587
# For custom SMTP: your-smtp-server.com, port 587 or 465
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Sender Email Credentials
# Note: For Gmail, you may need to use an "App Password" instead of your regular password
# To create an App Password: Gmail Settings > Security > 2-Step Verification > App Passwords
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
SENDER_NAME = "Commission Reconciliation System"

# Default Recipients
# Add the email addresses that should receive reports by default
DEFAULT_RECIPIENTS = [
    "owner@agency.com",
    "accounting@agency.com",
    "manager@agency.com"
]

# Email Settings
SEND_EMAIL_ENABLED = True  # Set to False to disable email sending
INCLUDE_ATTACHMENTS = True  # Set to False to send email without PDF attachment
EMAIL_SUBJECT_PREFIX = "[Commission Report]"  # Prefix for email subjects

# Environment Variable Alternative
# Instead of hardcoding credentials above, you can use environment variables:
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SENDER_EMAIL=your-email@gmail.com
# SENDER_PASSWORD=your-app-password
# SENDER_NAME=Commission System
# DEFAULT_RECIPIENTS=email1@domain.com,email2@domain.com