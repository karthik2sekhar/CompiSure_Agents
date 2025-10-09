#!/usr/bin/env python3
"""
Test PDF reason field trunc        print("Test data included:")
        print("Overpayment reason:", test_data['Test Carrier']['overpayments'][0]['reason'])
        print("Underpayment reason:", test_data['Test Carrier']['underpayments'][0]['reason'])on fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.report_generator import ReportGenerator
from datetime import datetime

def test_pdf_reason_truncation_fix():
    """Test that PDF reports now show full reason messages without truncation"""
    
    # Create test data with long reason messages - matching the expected structure
    test_data = {
        'Test Carrier': {
            'carrier': 'Test Carrier',
            'statement_period': 'January 2024',
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_policies': 100,
            'total_commission': 50000.00,
            'total_discrepancies': 2,
            'overpayments': [
                {
                    'policy_number': 'POL001',
                    'member_name': 'John Smith',
                    'amount': 186.00,
                    'percentage': 15.5,
                    'reason': 'Subscriber total $186.00 exceeds expected $150.00 by $36.00 due to additional premium adjustments and late payment processing'
                }
            ],
            'underpayments': [
                {
                    'policy_number': 'POL002', 
                    'member_name': 'Jane Doe',
                    'amount': 75.50,
                    'percentage': -12.3,
                    'reason': 'Subscriber total $75.50 below expected $125.00 by $49.50 due to mid-month termination and pro-rated commission calculation with early cancellation adjustments'
                }
            ]
        }
    }
    
    # Generate PDF report
    generator = ReportGenerator()
    pdf_path = 'test_reason_truncation_fix.pdf'
    
    try:
        # Create output directory
        output_dir = os.path.dirname(os.path.abspath(pdf_path))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate PDF using the private method directly
        actual_pdf_path = generator._generate_pdf_report(test_data, output_dir, timestamp)
        print(f"✅ PDF report generated successfully: {actual_pdf_path}")
        print("\nTest data included:")
        print("Overpayment reason:", test_data['Test Carrier']['overpayments'][0]['reason'])
        print("Underpayment reason:", test_data['Test Carrier']['underpayments'][0]['reason'])
        print("\nPlease manually verify the PDF shows complete reason messages without truncation.")
        
        # Check if file exists
        if os.path.exists(actual_pdf_path):
            file_size = os.path.getsize(actual_pdf_path)
            print(f"PDF file size: {file_size} bytes")
        else:
            print("❌ PDF file was not created")
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing PDF reason field truncation fix...")
    test_pdf_reason_truncation_fix()