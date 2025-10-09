#!/usr/bin/env python3
"""
Debug PDF Generation
Simple test with basic content to see what's working
"""

import sys
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def debug_pdf():
    """Create a simple PDF with basic content first"""
    
    filepath = "debug_simple.pdf"
    
    try:
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add basic content
        story.append(Paragraph("Debug PDF Test", styles['Heading1']))
        story.append(Paragraph("This is a test to verify basic PDF generation", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Add a simple table
        simple_data = [
            ['Column 1', 'Column 2', 'Column 3'],
            ['Row 1 Data', 'Row 1 Data', 'Row 1 Data'],
            ['Row 2 Data', 'Row 2 Data', 'Row 2 Data'],
            ['Row 3 Data', 'Row 3 Data', 'Row 3 Data']
        ]
        
        simple_table = Table(simple_data)
        simple_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(simple_table)
        story.append(Spacer(1, 12))
        
        # Add more content to make it larger
        for i in range(10):
            story.append(Paragraph(f"This is paragraph number {i+1}. " * 10, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Debug PDF generated: {filepath}")
        print(f"📄 Debug PDF size: {file_size:,} bytes")
        
        return file_size > 5000
        
    except Exception as e:
        print(f"❌ Debug PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_data_structure():
    """Check the data structure"""
    try:
        with open("reports/commission_reconciliation_data_20251006_144439.json", "r") as f:
            data = json.load(f)
        
        hc_data = data.get("hc", {})
        print(f"📋 HC data keys: {list(hc_data.keys())}")
        
        overpayments = hc_data.get("overpayments", [])
        print(f"📊 Overpayments count: {len(overpayments)}")
        if overpayments:
            print(f"📋 First overpayment keys: {list(overpayments[0].keys())}")
            print(f"📋 First overpayment sample: {overpayments[0]}")
        
        underpayments = hc_data.get("underpayments", [])
        print(f"📊 Underpayments count: {len(underpayments)}")
        if underpayments:
            print(f"📋 First underpayment keys: {list(underpayments[0].keys())}")
            print(f"📋 First underpayment sample: {underpayments[0]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Data structure check failed: {e}")
        return False

if __name__ == "__main__":
    print("=== DEBUG PDF GENERATION ===")
    
    print("\n1. Checking data structure:")
    debug_data_structure()
    
    print("\n2. Testing basic PDF generation:")
    pdf_success = debug_pdf()
    
    print(f"\n✅ Debug complete. Basic PDF works: {pdf_success}")
    
    sys.exit(0 if pdf_success else 1)