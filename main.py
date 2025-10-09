"""
Automated Commission Reconciliation System
Health Insurance Agency Commission Processing

This system automates the reconciliation of commission statements from multiple carriers,
performs variance analysis, and generates comprehensive reports.
"""

from src.commission_processor import CommissionProcessor
from src.reconciliation_engine import ReconciliationEngine
from src.report_generator import ReportGenerator
from src.email_service import EmailService
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/commission_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_reconciliation_workflow():
    """
    Run the complete commission reconciliation workflow
    Returns True if successful, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        processor = CommissionProcessor()
        reconciler = ReconciliationEngine()
        reporter = ReportGenerator()
        
        # Process commission statements
        logger.info("Processing commission statements from docs folder...")
        commission_data = processor.process_all_statements("docs")
        
        if not commission_data:
            logger.warning("No commission data found to process")
            return False
        
        # Perform reconciliation analysis
        logger.info("Performing reconciliation analysis...")
        reconciliation_results = reconciler.reconcile_commissions(commission_data)
        
        # Generate period-specific analysis
        logger.info("Generating period-specific analysis...")
        period_analysis = reconciler.generate_period_specific_analysis(reconciliation_results)
        
        # Add period analysis to results for reporting
        reconciliation_results['period_analysis'] = period_analysis
        
        # Log period-specific insights
        for period, summary in period_analysis.get('period_comparison', {}).items():
            logger.info(f"Period {period}: ${summary['total_actual']:.2f} actual vs ${summary['total_expected']:.2f} expected (Variance: ${summary['total_variance']:.2f})")
        
        # Generate reports
        logger.info("Generating reconciliation reports...")
        output_dir = "reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        report_files = reporter.generate_reports(reconciliation_results, output_dir)
        
        # Send email with PDF report
        logger.info("Attempting to send email report...")
        email_service = EmailService()
        
        # Find the PDF report file (use the enhanced detailed PDF)
        pdf_report = None
        for file in report_files:
            if file.endswith('.pdf') and 'commission_reconciliation_summary' in file.lower():
                pdf_report = file
                break
        
        # Fallback to any PDF if the enhanced one is not found
        if not pdf_report:
            for file in report_files:
                if file.endswith('.pdf'):
                    pdf_report = file
                    break
        
        if pdf_report:
            # Get email configuration from environment variables
            recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
            recipients = [email.strip() for email in recipients if email.strip()]
            
            if recipients:
                success = email_service.send_reconciliation_report(
                    pdf_report, 
                    recipients, 
                    reconciliation_results
                )
                if success:
                    logger.info(f"Email report sent successfully to: {', '.join(recipients)}")
                else:
                    logger.warning("Failed to send email report")
            else:
                logger.info("No email recipients configured. Set EMAIL_RECIPIENTS environment variable.")
        else:
            logger.warning("PDF report not found for email sending")
        
        logger.info("Commission reconciliation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error in commission reconciliation workflow: {str(e)}")
        return False


def main():
    """Main function to run the commission reconciliation process"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Automated Commission Reconciliation System")
    
    try:
        # Run the workflow
        success = run_reconciliation_workflow()
        
        if success:
            # Get the latest reconciliation results for summary display
            processor = CommissionProcessor()
            reconciler = ReconciliationEngine()
            
            commission_data = processor.process_all_statements("docs")
            if commission_data:
                reconciliation_results = reconciler.reconcile_commissions(commission_data)
                
                # Display summary
                print("\n" + "="*60)
                print("COMMISSION RECONCILIATION SUMMARY")
                print("="*60)
                
                for carrier, results in reconciliation_results.items():
                    print(f"\n{carrier.upper()}:")
                    
                    # Handle different field names for different analysis types
                    if carrier == 'cross_carrier_analysis':
                        total_commissions = results.get('total_all_carriers', 0)
                    else:
                        total_commissions = results.get('total_commissions', 0)
                        
                    print(f"  Total Commissions: ${total_commissions:,.2f}")
                    print(f"  Discrepancies Found: {len(results.get('discrepancies', []))}")
                    print(f"  Variance Amount: ${results.get('variance_amount', 0):,.2f}")
                    
                    # Also show overpayments and underpayments summary
                    overpayments = results.get('overpayments', [])
                    underpayments = results.get('underpayments', [])
                    if overpayments:
                        total_overpaid = sum(op.get('amount', 0) for op in overpayments)
                        print(f"  Overpayments: {len(overpayments)} policies, ${total_overpaid:,.2f}")
                    if underpayments:
                        total_underpaid = sum(up.get('amount', 0) for up in underpayments)
                        print(f"  Underpayments: {len(underpayments)} policies, ${total_underpaid:,.2f}")
                
                print(f"\nDetailed reports saved to: reports")
                print("="*60)
        
    except Exception as e:
        logger.error(f"Error in commission reconciliation: {str(e)}")
        raise

if __name__ == "__main__":
    main()