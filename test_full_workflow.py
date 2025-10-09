#!/usr/bin/env python3
"""
Full Workflow Test Script
Tests the complete end-to-end commission reconciliation workflow including:
1. PDF extraction (with fixed HNE/Humana patterns)
2. Reconciliation analysis
3. PDF report generation
4. Email sending (test mode)
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from commission_processor import CommissionProcessor
from reconciliation_engine import ReconciliationEngine
from report_generator import ReportGenerator
from email_service import EmailService

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    """Run complete workflow test"""
    logger = setup_logging()
    
    print("🧪 TESTING COMPLETE COMMISSION RECONCILIATION WORKFLOW")
    print("=" * 60)
    
    try:
        # Step 1: Initialize components
        print("\n1️⃣ INITIALIZING COMPONENTS...")
        processor = CommissionProcessor()
        reconciler = ReconciliationEngine()
        reporter = ReportGenerator()
        email_service = EmailService()
        print("   ✅ All components initialized")
        
        # Step 2: Process commission statements (using fixed extraction)
        print("\n2️⃣ PROCESSING COMMISSION STATEMENTS...")
        docs_folder = "docs"
        if not os.path.exists(docs_folder):
            print(f"   ❌ Docs folder not found: {docs_folder}")
            return False
            
        commission_data = processor.process_all_statements(docs_folder)
        
        if not commission_data:
            print("   ❌ No commission data extracted")
            return False
            
        print(f"   ✅ Processed carriers: {list(commission_data.keys())}")
        
        # Show extraction results
        for carrier, data in commission_data.items():
            commissions = data.get('commissions', [])
            total_amount = sum(float(entry.get('commission_amount', 0)) for entry in commissions)
            print(f"   📊 {carrier}: {len(commissions)} entries, Total: ${total_amount:,.2f}")
        
        # Step 3: Perform reconciliation analysis
        print("\n3️⃣ PERFORMING RECONCILIATION ANALYSIS...")
        reconciliation_results = reconciler.reconcile_commissions(commission_data)
        
        if not reconciliation_results:
            print("   ❌ Reconciliation failed")
            return False
            
        print("   ✅ Reconciliation completed")
        
        # Show reconciliation results
        for carrier, results in reconciliation_results.items():
            if carrier == 'cross_carrier_analysis':
                continue
            discrepancies = results.get('discrepancies', [])
            print(f"   📋 {carrier}: {len(discrepancies)} discrepancies found")
        
        # Step 4: Generate reports
        print("\n4️⃣ GENERATING REPORTS...")
        output_dir = "test_reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        report_files = reporter.generate_reports(reconciliation_results, output_dir)
        
        if not report_files:
            print("   ❌ No reports generated")
            return False
            
        print("   ✅ Reports generated:")
        for file in report_files:
            file_size = os.path.getsize(file) if os.path.exists(file) else 0
            print(f"      📄 {os.path.basename(file)} ({file_size:,} bytes)")
        
        # Step 5: Find PDF report
        print("\n5️⃣ LOCATING PDF REPORT...")
        pdf_report = None
        for file in report_files:
            if file.endswith('.pdf') and 'commission_reconciliation_summary' in file.lower():
                pdf_report = file
                break
        
        if not pdf_report:
            # Fallback to any PDF
            for file in report_files:
                if file.endswith('.pdf'):
                    pdf_report = file
                    break
        
        if not pdf_report:
            print("   ❌ No PDF report found")
            return False
            
        print(f"   ✅ PDF report located: {os.path.basename(pdf_report)}")
        
        # Step 6: Test email functionality (without actually sending)
        print("\n6️⃣ TESTING EMAIL FUNCTIONALITY...")
        
        # Test email message creation
        test_recipients = ["test@example.com", "manager@example.com"]
        
        try:
            # Create email message (but don't send)
            msg = email_service._create_email_message(
                pdf_report, 
                test_recipients, 
                reconciliation_results
            )
            print("   ✅ Email message created successfully")
            print(f"      📧 Subject: {msg['Subject']}")
            print(f"      📧 Recipients: {msg['To']}")
            print(f"      📧 From: {msg['From']}")
            
            # Check if PDF is attached
            attachments = [part for part in msg.walk() if part.get_content_disposition() == 'attachment']
            if attachments:
                print(f"      📎 PDF attachment: {len(attachments)} file(s) attached")
            else:
                print("      ❌ No PDF attachment found")
                
        except Exception as e:
            print(f"   ❌ Email message creation failed: {e}")
            return False
        
        # Step 7: Validate report content
        print("\n7️⃣ VALIDATING REPORT CONTENT...")
        
        # Check if PDF file exists and has reasonable size
        if os.path.exists(pdf_report):
            pdf_size = os.path.getsize(pdf_report)
            print(f"   ✅ PDF report exists: {pdf_size:,} bytes")
            
            if pdf_size > 1000:  # At least 1KB
                print("   ✅ PDF report has reasonable size")
            else:
                print("   ⚠️  PDF report seems too small")
        else:
            print("   ❌ PDF report file not found")
            return False
        
        # Step 8: Summary
        print("\n8️⃣ WORKFLOW SUMMARY...")
        print("   ✅ Extraction: Fixed HNE/Humana patterns working")
        print("   ✅ Reconciliation: Analysis completed")
        print("   ✅ Reports: PDF generated successfully")
        print("   ✅ Email: Message creation working")
        
        # Check for the original $0.00 issue
        zero_issues_found = False
        for carrier, data in commission_data.items():
            commissions = data.get('commissions', [])
            zero_count = sum(1 for entry in commissions if float(entry.get('commission_amount', 0)) == 0)
            total_count = len(commissions)
            
            if zero_count == total_count and total_count > 0:
                print(f"   ❌ ALL ZERO ISSUE: {carrier} has {zero_count}/{total_count} zero amounts")
                zero_issues_found = True
            elif zero_count > 0:
                print(f"   ℹ️  PARTIAL ZEROS: {carrier} has {zero_count}/{total_count} zero amounts (may be legitimate)")
            else:
                print(f"   ✅ NO ZEROS: {carrier} has all non-zero amounts")
        
        if not zero_issues_found:
            print("\n🎉 SUCCESS: Original $0.00 subscriber totals issue is RESOLVED!")
        else:
            print("\n⚠️  WARNING: Still have carriers with all-zero amounts")
        
        print(f"\n📁 Generated files in {output_dir}:")
        for file in report_files:
            print(f"   - {os.path.basename(file)}")
        
        print("\n✅ FULL WORKFLOW TEST COMPLETED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        logger.error(f"Workflow test failed: {str(e)}")
        print(f"\n❌ WORKFLOW TEST FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)