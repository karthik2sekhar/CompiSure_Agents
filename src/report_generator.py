"""
Report Generator Module
Generates comprehensive reconciliation reports in multiple formats
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
import logging
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class ReportGenerator:
    """Generates comprehensive commission reconciliation reports"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        sns.set_style("whitegrid")
        plt.style.use('default')
    
    def generate_reports(self, reconciliation_results: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Generate all reconciliation reports
        
        Args:
            reconciliation_results: Results from reconciliation analysis
            output_dir: Directory to save reports
            
        Returns:
            List of generated report file paths
        """
        report_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Generate Excel summary report
            excel_file = self._generate_excel_report(reconciliation_results, output_dir, timestamp)
            if excel_file:
                report_files.append(excel_file)
            
            # Generate detailed HTML report
            html_file = self._generate_html_report(reconciliation_results, output_dir, timestamp)
            if html_file:
                report_files.append(html_file)
            
            # Generate PDF executive summary
            pdf_file = self._generate_pdf_report(reconciliation_results, output_dir, timestamp)
            if pdf_file:
                report_files.append(pdf_file)
            
            # Generate JSON data export
            json_file = self._generate_json_export(reconciliation_results, output_dir, timestamp)
            if json_file:
                report_files.append(json_file)
            
            # Generate visualization charts
            chart_files = self._generate_charts(reconciliation_results, output_dir, timestamp)
            report_files.extend(chart_files)
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {str(e)}")
        
        return report_files
    
    def _generate_excel_report(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate comprehensive Excel report with multiple sheets"""
        filename = f"commission_reconciliation_report_{timestamp}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                for carrier, data in results.items():
                    if carrier == 'cross_carrier_analysis':
                        continue
                    
                    summary_data.append({
                        'Carrier': carrier.replace('_', ' ').title(),
                        'Total Commissions': data.get('total_commissions', 0),
                        'Expected Commissions': data.get('expected_commissions', 0),
                        'Variance Amount': data.get('variance_amount', 0),
                        'Variance %': data.get('variance_percentage', 0),
                        'Discrepancies Count': len(data.get('discrepancies', [])),
                        'Overpayments': len([d for d in data.get('discrepancies', []) if d.get('type') == 'overpayment']),
                        'Underpayments': len([d for d in data.get('discrepancies', []) if d.get('type') == 'underpayment'])
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Individual carrier sheets
                for carrier, data in results.items():
                    if carrier == 'cross_carrier_analysis':
                        continue
                    
                    sheet_name = carrier.replace('_', ' ').title()[:31]  # Excel sheet name limit
                    
                    # Create carrier detail sheet
                    carrier_data = []
                    
                    # Add summary info
                    carrier_data.append(['Metric', 'Value'])
                    carrier_data.append(['Total Commissions', f"${data.get('total_commissions', 0):,.2f}"])
                    carrier_data.append(['Expected Commissions', f"${data.get('expected_commissions', 0):,.2f}"])
                    carrier_data.append(['Variance Amount', f"${data.get('variance_amount', 0):,.2f}"])
                    carrier_data.append(['Variance Percentage', f"{data.get('variance_percentage', 0):.2f}%"])
                    carrier_data.append(['', ''])  # Empty row
                    
                    # Add discrepancies
                    if data.get('discrepancies'):
                        carrier_data.append(['Discrepancies', ''])
                        carrier_data.append(['Type', 'Amount', 'Details'])
                        
                        for disc in data.get('discrepancies', []):
                            carrier_data.append([
                                disc.get('type', ''),
                                f"${disc.get('amount', 0):,.2f}",
                                disc.get('reason', '')
                            ])
                    
                    carrier_df = pd.DataFrame(carrier_data)
                    carrier_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                
                # Cross-carrier analysis sheet
                if 'cross_carrier_analysis' in results:
                    cross_data = results['cross_carrier_analysis']
                    cross_rows = []
                    
                    cross_rows.append(['Cross-Carrier Analysis', ''])
                    cross_rows.append(['Total All Carriers', f"${cross_data.get('total_all_carriers', 0):,.2f}"])
                    cross_rows.append(['', ''])
                    
                    if 'carrier_comparison' in cross_data:
                        cross_rows.append(['Carrier', 'Amount', 'Percentage'])
                        for carrier, comp_data in cross_data['carrier_comparison'].items():
                            cross_rows.append([
                                carrier.replace('_', ' ').title(),
                                f"${comp_data.get('amount', 0):,.2f}",
                                f"{comp_data.get('percentage', 0):.1f}%"
                            ])
                    
                    cross_df = pd.DataFrame(cross_rows)
                    cross_df.to_excel(writer, sheet_name='Cross-Carrier Analysis', index=False, header=False)
            
            self.logger.info(f"Excel report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating Excel report: {str(e)}")
            return ""
    
    def _generate_html_report(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate detailed HTML report"""
        filename = f"commission_reconciliation_report_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Commission Reconciliation Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }
                .summary { background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }
                .carrier-section { margin: 30px 0; border: 1px solid #ddd; border-radius: 5px; }
                .carrier-header { background-color: #e9ecef; padding: 15px; font-weight: bold; }
                .carrier-content { padding: 15px; }
                table { width: 100%; border-collapse: collapse; margin: 15px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .metric { display: inline-block; margin: 10px 20px 10px 0; }
                .metric-label { font-weight: bold; }
                .positive { color: green; }
                .negative { color: red; }
                .warning { color: orange; }
                .discrepancy { background-color: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Commission Reconciliation Report</h1>
                <p>Generated on {{ report_date }}</p>
            </div>
            
            <div class="summary">
                <h2>Executive Summary</h2>
                {% if cross_carrier_analysis %}
                <div class="metric">
                    <span class="metric-label">Total Commission (All Carriers):</span> 
                    ${{ "%.2f"|format(cross_carrier_analysis.total_all_carriers) }}
                </div>
                {% endif %}
                
                <div class="metric">
                    <span class="metric-label">Carriers Processed:</span> {{ carrier_count }}
                </div>
                
                <div class="metric">
                    <span class="metric-label">Total Discrepancies:</span> {{ total_discrepancies }}
                </div>
            </div>
            
            {% for carrier, data in carriers.items() %}
            <div class="carrier-section">
                <div class="carrier-header">
                    {{ carrier.replace('_', ' ').title() }} Commission Analysis
                </div>
                <div class="carrier-content">
                    <div class="metric">
                        <span class="metric-label">Total Commissions:</span> 
                        ${{ "%.2f"|format(data.total_commissions) }}
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Expected Commissions:</span> 
                        ${{ "%.2f"|format(data.expected_commissions) }}
                    </div>
                    
                    <div class="metric">
                        <span class="metric-label">Variance:</span> 
                        <span class="{% if data.variance_amount > 0 %}positive{% elif data.variance_amount < 0 %}negative{% endif %}">
                            ${{ "%.2f"|format(data.variance_amount) }} ({{ "%.1f"|format(data.variance_percentage) }}%)
                        </span>
                    </div>
                    
                    {% if data.discrepancies %}
                    <h4>Discrepancies Found:</h4>
                    {% for disc in data.discrepancies %}
                    <div class="discrepancy">
                        <strong>{{ disc.type|title }}:</strong> 
                        {% if disc.policy_number %}
                            Policy {{ disc.policy_number }} - 
                        {% endif %}
                        {% if disc.variance_amount %}
                            Expected: ${{ "%.2f"|format(disc.expected_amount) }}, 
                            Actual: ${{ "%.2f"|format(disc.actual_amount) }}, 
                            Variance: ${{ "%.2f"|format(disc.variance_amount) }}
                        {% else %}
                            ${{ "%.2f"|format(disc.amount) }} - {{ disc.reason }}
                        {% endif %}
                    </div>
                    {% endfor %}
                    {% endif %}
                    
                    {% if data.year_to_date and data.year_to_date.monthly_breakdown %}
                    <h4>Year-to-Date Monthly Breakdown:</h4>
                    <table>
                        <tr><th>Month</th><th>Commission Amount</th></tr>
                        {% for month, amount in data.year_to_date.monthly_breakdown.items() %}
                        <tr><td>{{ month }}</td><td>${{ "%.2f"|format(amount) }}</td></tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
            
            <div style="margin-top: 50px; text-align: center; color: #666; font-size: 12px;">
                <p>Generated by Automated Commission Reconciliation System</p>
            </div>
        </body>
        </html>
        """
        
        try:
            # Prepare template data
            template_data = {
                'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'carriers': {k: v for k, v in results.items() if k != 'cross_carrier_analysis'},
                'cross_carrier_analysis': results.get('cross_carrier_analysis', {}),
                'carrier_count': len([k for k in results.keys() if k != 'cross_carrier_analysis']),
                'total_discrepancies': sum(len(v.get('discrepancies', [])) for k, v in results.items() if k != 'cross_carrier_analysis')
            }
            
            template = Template(html_template)
            html_content = template.render(**template_data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {str(e)}")
            return ""
    
    def _generate_pdf_report(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate PDF executive summary report"""
        filename = f"commission_reconciliation_summary_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph("Commission Reconciliation Report", title_style))
            story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            
            if 'cross_carrier_analysis' in results:
                cross_data = results['cross_carrier_analysis']
                summary_text = f"""
                Total Commission Processed: ${cross_data.get('total_all_carriers', 0):,.2f}<br/>
                Number of Carriers: {len([k for k in results.keys() if k != 'cross_carrier_analysis'])}<br/>
                Total Discrepancies: {sum(len(v.get('discrepancies', [])) for k, v in results.items() if k != 'cross_carrier_analysis')}
                """
                story.append(Paragraph(summary_text, styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Carrier breakdown table
            story.append(Paragraph("Carrier Summary", styles['Heading2']))
            
            table_data = [['Carrier', 'Total Commissions', 'Variance Amount', 'Discrepancies']]
            
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis':
                    continue
                
                table_data.append([
                    carrier.replace('_', ' ').title(),
                    f"${data.get('total_commissions', 0):,.2f}",
                    f"${data.get('variance_amount', 0):,.2f}",
                    str(len(data.get('discrepancies', [])))
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Individual carrier details
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis':
                    continue
                
                story.append(Paragraph(f"{carrier.replace('_', ' ').title()} Details", styles['Heading3']))
                
                details_text = f"""
                Total Commissions: ${data.get('total_commissions', 0):,.2f}<br/>
                Expected Commissions: ${data.get('expected_commissions', 0):,.2f}<br/>
                Variance: ${data.get('variance_amount', 0):,.2f} ({data.get('variance_percentage', 0):.1f}%)<br/>
                """
                
                story.append(Paragraph(details_text, styles['Normal']))
                
                if data.get('discrepancies'):
                    story.append(Paragraph("Discrepancies:", styles['Heading4']))
                    for disc in data.get('discrepancies', []):
                        # Use the correct field names from the discrepancy data structure
                        disc_type = disc.get('type', '').title()
                        actual_amount = disc.get('actual_amount', 0)
                        expected_amount = disc.get('expected_amount', 0)
                        variance_amount = disc.get('variance_amount', 0)
                        variance_pct = disc.get('variance_percentage', 0)
                        
                        disc_text = f"• {disc_type}: ${abs(variance_amount):,.2f} - Commission variance: Expected ${expected_amount:.2f}, Actual ${actual_amount:.2f}, Variance ${variance_amount:.2f} ({variance_pct:.1f}%)"
                        story.append(Paragraph(disc_text, styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            doc.build(story)
            self.logger.info(f"PDF report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            return ""
    
    def _generate_json_export(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> str:
        """Generate JSON export of all reconciliation data"""
        filename = f"commission_reconciliation_data_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        try:
            # Convert numpy types to Python native types for JSON serialization
            def convert_types(obj):
                if hasattr(obj, 'item'):
                    return obj.item()
                elif isinstance(obj, dict):
                    return {k: convert_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_types(v) for v in obj]
                else:
                    return obj
            
            clean_results = convert_types(results)
            
            with open(filepath, 'w') as f:
                json.dump(clean_results, f, indent=2, default=str)
            
            self.logger.info(f"JSON export generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error generating JSON export: {str(e)}")
            return ""
    
    def _generate_charts(self, results: Dict[str, Any], output_dir: str, timestamp: str) -> List[str]:
        """Generate visualization charts"""
        chart_files = []
        
        try:
            # Commission by carrier pie chart
            if 'cross_carrier_analysis' in results and results['cross_carrier_analysis'].get('carrier_breakdown'):
                carrier_data = results['cross_carrier_analysis']['carrier_breakdown']
                
                plt.figure(figsize=(10, 8))
                carriers = [k.replace('_', ' ').title() for k in carrier_data.keys()]
                amounts = list(carrier_data.values())
                
                plt.pie(amounts, labels=carriers, autopct='%1.1f%%', startangle=90)
                plt.title('Commission Distribution by Carrier', fontsize=16, fontweight='bold')
                
                chart_file = os.path.join(output_dir, f"commission_by_carrier_{timestamp}.png")
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                chart_files.append(chart_file)
                self.logger.info(f"Pie chart generated: {chart_file}")
            
            # Variance analysis bar chart
            carriers = []
            variances = []
            
            for carrier, data in results.items():
                if carrier == 'cross_carrier_analysis':
                    continue
                
                carriers.append(carrier.replace('_', ' ').title())
                variances.append(data.get('variance_amount', 0))
            
            if carriers and variances:
                plt.figure(figsize=(12, 6))
                colors_list = ['green' if v >= 0 else 'red' for v in variances]
                
                plt.bar(carriers, variances, color=colors_list, alpha=0.7)
                plt.title('Commission Variance by Carrier', fontsize=16, fontweight='bold')
                plt.xlabel('Carrier')
                plt.ylabel('Variance Amount ($)')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for i, v in enumerate(variances):
                    plt.text(i, v + (max(variances) * 0.01), f'${v:,.0f}', 
                            ha='center', va='bottom', fontweight='bold')
                
                chart_file = os.path.join(output_dir, f"variance_analysis_{timestamp}.png")
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                chart_files.append(chart_file)
                self.logger.info(f"Bar chart generated: {chart_file}")
        
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
        
        return chart_files