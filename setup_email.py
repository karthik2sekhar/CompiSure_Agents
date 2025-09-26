"""
One-time Email Configuration Setup
Run this script once to set up your email configuration permanently
"""

import os
from dotenv import load_dotenv, set_key

def setup_email_config():
    """Interactive setup for email configuration"""
    print("=" * 60)
    print("Commission Statement Auto-Monitor - Email Setup")
    print("=" * 60)
    print()
    
    env_file = ".env"
    
    # Load existing config if it exists
    if os.path.exists(env_file):
        load_dotenv()
        print("📁 Found existing .env file. Current settings:")
        print(f"   SENDER_EMAIL: {os.getenv('SENDER_EMAIL', 'Not set')}")
        print(f"   EMAIL_RECIPIENTS: {os.getenv('EMAIL_RECIPIENTS', 'Not set')}")
        print(f"   SENDER_PASSWORD: {'Set' if os.getenv('SENDER_PASSWORD') else 'Not set'}")
        print(f"   OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
        print()
        
        update = input("Do you want to update these settings? (y/n): ").lower().strip()
        if update != 'y':
            print("Configuration unchanged.")
            return
    
    print("Please enter your email configuration:")
    print()
    
    # Get sender email
    current_sender = os.getenv('SENDER_EMAIL', '')
    sender_email = input(f"Your Gmail address [{current_sender}]: ").strip()
    if not sender_email and current_sender:
        sender_email = current_sender
    elif not sender_email:
        sender_email = input("Your Gmail address (required): ").strip()
    
    # Get sender password
    print("\n🔑 Gmail App Password Setup:")
    print("   1. Go to Google Account settings")
    print("   2. Security → 2-Factor Authentication (must be enabled)")
    print("   3. App Passwords → Generate App Password")
    print("   4. Select 'Mail' and 'Windows Computer'")
    print("   5. Copy the 16-character password")
    print()
    
    sender_password = input("Your Gmail App Password (16 characters): ").strip().replace(" ", "")
    
    # Get recipients
    current_recipients = os.getenv('EMAIL_RECIPIENTS', '')
    recipients = input(f"Email recipients (comma-separated) [{current_recipients}]: ").strip()
    if not recipients and current_recipients:
        recipients = current_recipients
    elif not recipients:
        recipients = sender_email  # Default to sender
    
    # Get sender name
    current_name = os.getenv('SENDER_NAME', 'Commission Reconciliation System')
    sender_name = input(f"Sender name [{current_name}]: ").strip()
    if not sender_name:
        sender_name = current_name
    
    # Get OpenAI API key
    print("\n🤖 OpenAI API Key Setup (optional but recommended):")
    print("   1. Go to https://platform.openai.com/api-keys")
    print("   2. Create a new API key")
    print("   3. Copy the API key (starts with 'sk-')")
    print("   4. This enables AI-powered PDF extraction for better accuracy")
    print("   5. Leave blank to skip (system will use regex patterns)")
    print()
    
    current_openai_key = os.getenv('OPENAI_API_KEY', '')
    openai_key = input(f"OpenAI API Key (optional) [{'Set' if current_openai_key else 'Not set'}]: ").strip()
    if not openai_key and current_openai_key:
        openai_key = current_openai_key
    
    # Save to .env file
    print("\n💾 Saving configuration...")
    
    set_key(env_file, "SENDER_EMAIL", sender_email)
    set_key(env_file, "SENDER_PASSWORD", sender_password)
    set_key(env_file, "EMAIL_RECIPIENTS", recipients)
    set_key(env_file, "SENDER_NAME", sender_name)
    set_key(env_file, "SMTP_SERVER", "smtp.gmail.com")
    set_key(env_file, "SMTP_PORT", "587")
    
    if openai_key:
        set_key(env_file, "OPENAI_API_KEY", openai_key)
        ai_status = "✅ AI-powered extraction enabled"
    else:
        ai_status = "⚠️ Using regex patterns (AI extraction disabled)"
    
    print("✅ Configuration saved successfully!")
    print()
    print("📧 Your settings:")
    print(f"   Sender: {sender_name} <{sender_email}>")
    print(f"   Recipients: {recipients}")
    print(f"   🤖 AI Processing: {ai_status}")
    print(f"   SMTP: smtp.gmail.com:587")
    print()
    print("🚀 You can now start the monitor and it will automatically send emails!")
    print("   Just run: python monitor_commissions.py")
    print()

if __name__ == "__main__":
    try:
        setup_email_config()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    except Exception as e:
        print(f"\nError during setup: {e}")
        print("Please check your inputs and try again.")