"""
Email Service Module
Handles sending PDF reports via email with attachments and HTML content
"""

import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


class EmailService:
    """Service for sending commission reconciliation reports via email"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def send_reconciliation_report(
        self,
        pdf_path: str,
        recipients: List[str],
        reconciliation_results: Dict[str, Any],
        smtp_config: Dict[str, str] = None
    ) -> bool:
        """
        Send PDF reconciliation report via email
        
        Args:
            pdf_path: Path to the PDF report file
            recipients: List of email addresses to send to
            reconciliation_results: Results from reconciliation analysis
            smtp_config: SMTP configuration dictionary
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Use default SMTP config if none provided
            if smtp_config is None:
                smtp_config = self._get_default_smtp_config()
            
            # Validate inputs
            if not os.path.exists(pdf_path):
                self.logger.error(f"PDF file not found: {pdf_path}")
                return False
                
            if not recipients:
                self.logger.error("No recipients specified")
                return False
            
            # Create email message
            msg = self._create_email_message(pdf_path, recipients, reconciliation_results)
            
            # Send email
            return self._send_email(msg, smtp_config)
            
        except Exception as e:
            self.logger.error(f"Error sending reconciliation report: {e}")
            return False
    
    def _get_default_smtp_config(self) -> Dict[str, str]:
        """Get default SMTP configuration from environment variables"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', ''),
            'sender_name': os.getenv('SENDER_NAME', 'Commission Reconciliation System')
        }
    
    def _create_email_message(
        self,
        pdf_path: str,
        recipients: List[str],
        reconciliation_results: Dict[str, Any]
    ) -> MIMEMultipart:
        """Create email message with PDF attachment and HTML content"""
        
        # Create message
        msg = MIMEMultipart('alternative')
        
        # Email headers
        msg['From'] = f"{self._get_default_smtp_config()['sender_name']} <{self._get_default_smtp_config()['sender_email']}>"
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = self._generate_subject(reconciliation_results)
        
        # Create HTML body
        html_body = self._generate_html_body(reconciliation_results)
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Create plain text alternative
        text_body = self._generate_text_body(reconciliation_results)
        text_part = MIMEText(text_body, 'plain')
        msg.attach(text_part)
        
        # Attach PDF
        self._attach_pdf(msg, pdf_path)
        
        return msg
    
    def _generate_subject(self, reconciliation_results: Dict[str, Any]) -> str:
        """Generate email subject line"""
        # Exclude non-carrier entries from count
        excluded_keys = {'cross_carrier_analysis', 'period_analysis'}
        total_carriers = len([k for k in reconciliation_results.keys() if k not in excluded_keys])
        
        # Count all discrepancies from all carriers (including empty lists)
        total_discrepancies = sum(len(v.get('discrepancies', [])) 
                                 for k, v in reconciliation_results.items() 
                                 if isinstance(v, dict) and k not in excluded_keys)
        
        date_str = datetime.now().strftime("%B %d, %Y")
        return f"Commission Reconciliation Report - {date_str} ({total_carriers} Carriers, {total_discrepancies} Discrepancies)"
    
    def _generate_html_body(self, reconciliation_results: Dict[str, Any]) -> str:
        """Generate HTML email body"""
        
        # Calculate summary statistics - exclude non-carrier entries
        excluded_keys = {'cross_carrier_analysis', 'period_analysis'}
        total_carriers = len([k for k in reconciliation_results.keys() if k not in excluded_keys])
        
        # Count all discrepancies from all carriers (including empty lists)
        total_discrepancies = sum(len(v.get('discrepancies', [])) 
                                 for k, v in reconciliation_results.items() 
                                 if isinstance(v, dict) and k not in excluded_keys)
        
        # Get cross-carrier total
        cross_analysis = reconciliation_results.get('cross_carrier_analysis', {})
        total_commissions = cross_analysis.get('total_all_carriers', 0)
        
        # Build carrier summaries - exclude non-carrier entries
        carrier_summaries = []
        excluded_keys = {'cross_carrier_analysis', 'period_analysis'}
        for carrier, results in reconciliation_results.items():
            if carrier not in excluded_keys and isinstance(results, dict):
                carrier_total = results.get('total_commissions', 0)
                variance = results.get('variance_amount', 0)
                discrepancy_count = len(results.get('discrepancies', []))
                
                status_color = "red" if variance != 0 else "green"
                status_text = f"${abs(variance):,.2f} {'Overpaid' if variance > 0 else 'Underpaid'}" if variance != 0 else "Balanced"
                
                carrier_summaries.append(f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{carrier.upper()}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">${carrier_total:,.2f}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{discrepancy_count}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: {status_color}; text-align: right;">{status_text}</td>
                </tr>
                """)
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #2c5aa0; }}
                .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
                .metric-label {{ font-size: 14px; color: #666; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background-color: #2c5aa0; color: white; padding: 12px; text-align: left; }}
                .footer {{ color: #666; font-size: 12px; text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Commission Reconciliation Report</h1>
                <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
            </div>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="metric">
                    <div class="metric-value">${total_commissions:,.2f}</div>
                    <div class="metric-label">Total Commissions</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{total_carriers}</div>
                    <div class="metric-label">Carriers Processed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{total_discrepancies}</div>
                    <div class="metric-label">Total Discrepancies</div>
                </div>
            </div>
            
            <h2>Carrier Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Carrier</th>
                        <th>Total Commissions</th>
                        <th>Discrepancies</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(carrier_summaries)}
                </tbody>
            </table>
            
            <div class="footer">
                <p><strong>Attached:</strong> Detailed PDF reconciliation report with complete analysis</p>
                <p>This report was generated automatically by the Commission Reconciliation System</p>
                <p>For technical support or questions, please contact your system administrator</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _generate_text_body(self, reconciliation_results: Dict[str, Any]) -> str:
        """Generate plain text email body"""
        
        lines = [
            "COMMISSION RECONCILIATION REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            "",
            "EXECUTIVE SUMMARY:",
        ]
        
        # Add summary statistics - exclude non-carrier entries
        excluded_keys = {'cross_carrier_analysis', 'period_analysis'}
        total_carriers = len([k for k in reconciliation_results.keys() if k not in excluded_keys])
        
        # Count all discrepancies from all carriers (including empty lists)
        total_discrepancies = sum(len(v.get('discrepancies', [])) 
                                 for k, v in reconciliation_results.items() 
                                 if isinstance(v, dict) and k not in excluded_keys)
        cross_analysis = reconciliation_results.get('cross_carrier_analysis', {})
        total_commissions = cross_analysis.get('total_all_carriers', 0)
        
        lines.extend([
            f"  Total Commissions: ${total_commissions:,.2f}",
            f"  Carriers Processed: {total_carriers}",
            f"  Total Discrepancies: {total_discrepancies}",
            "",
            "CARRIER BREAKDOWN:",
        ])
        
        # Add carrier details - exclude non-carrier entries
        excluded_keys = {'cross_carrier_analysis', 'period_analysis'}
        for carrier, results in reconciliation_results.items():
            if carrier not in excluded_keys and isinstance(results, dict):
                carrier_total = results.get('total_commissions', 0)
                variance = results.get('variance_amount', 0)
                discrepancy_count = len(results.get('discrepancies', []))
                
                status = f"${abs(variance):,.2f} {'Overpaid' if variance > 0 else 'Underpaid'}" if variance != 0 else "Balanced"
                
                lines.extend([
                    f"  {carrier.upper()}:",
                    f"    Total: ${carrier_total:,.2f}",
                    f"    Discrepancies: {discrepancy_count}",
                    f"    Status: {status}",
                    ""
                ])
        
        lines.extend([
            "ATTACHED FILES:",
            "  - Detailed PDF reconciliation report",
            "",
            "This report was generated automatically by the Commission Reconciliation System.",
            "For questions, please contact your system administrator."
        ])
        
        return "\n".join(lines)
    
    def _attach_pdf(self, msg: MIMEMultipart, pdf_path: str) -> None:
        """Attach PDF file to email message"""
        try:
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            
            filename = os.path.basename(pdf_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            self.logger.error(f"Error attaching PDF: {e}")
            raise
    
    def _send_email(self, msg: MIMEMultipart, smtp_config: Dict[str, str]) -> bool:
        """Send email using SMTP"""
        try:
            # Validate SMTP config
            required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password']
            for field in required_fields:
                if not smtp_config.get(field):
                    self.logger.error(f"Missing SMTP configuration: {field}")
                    return False
            
            # Create SMTP session
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()  # Enable TLS encryption
            server.login(smtp_config['sender_email'], smtp_config['sender_password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(smtp_config['sender_email'], msg['To'].split(', '), text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to: {msg['To']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def send_test_email(self, recipient: str, smtp_config: Dict[str, str] = None) -> bool:
        """Send a test email to verify configuration"""
        try:
            if smtp_config is None:
                smtp_config = self._get_default_smtp_config()
            
            msg = MIMEMultipart()
            msg['From'] = f"{smtp_config['sender_name']} <{smtp_config['sender_email']}>"
            msg['To'] = recipient
            msg['Subject'] = "Commission Reconciliation System - Test Email"
            
            body = """
            This is a test email from the Commission Reconciliation System.
            
            If you receive this email, the email configuration is working correctly.
            
            System Status: ✅ Ready
            Email Service: ✅ Operational
            
            Best regards,
            Commission Reconciliation System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            return self._send_email(msg, smtp_config)
            
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            return False