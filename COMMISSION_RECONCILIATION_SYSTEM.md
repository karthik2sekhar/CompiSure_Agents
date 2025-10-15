# Commission Reconciliation System - Complete Documentation

## 🎯 System Overview

The Commission Reconciliation System is a comprehensive solution for processing commission statements from multiple insurance carriers using saved LandingAI JSON responses. The system implements strict matching logic requiring both member ID and effective date to match exactly between commission statements and enrollment data.

### Key Features
- ✅ **Strict Matching Logic**: Requires exact member ID AND effective date match
- 🏥 **Multi-Carrier Support**: Extensible to support multiple insurance carriers
- 📧 **Automated Email Reports**: Sends detailed reports to stakeholders
- 📊 **Comprehensive Reporting**: Generates detailed text and JSON reports
- 🔄 **No API Calls**: Uses only saved LandingAI responses
- 📅 **Production Ready**: Includes automation, logging, and error handling

## 📁 File Structure

```
project_root/
├── commission_reconciliation_system.py      # Main system class
├── commission_reconciliation_automation.py  # Production automation script
├── commission_reconciliation_demo.py        # Demo and examples
├── run_commission_reconciliation.bat        # Windows automation batch file
├── COMMISSION_RECONCILIATION_CONFIG.md      # Configuration guide
├── landingai_system_responses/              # Saved LandingAI JSON responses
│   └── HNE_comm_system_response_*.json
├── docs/
│   └── enrollment_info.csv                  # Enrollment data
├── commission_reconciliation_reports/       # Generated reports
│   ├── archive/                             # Archived old reports
│   ├── *_commission_report_*.txt            # Text reports
│   ├── *_commission_data_*.json             # JSON data
│   └── commission_reconciliation_summary_*.json
└── logs/
    └── commission_reconciliation_*.log       # System logs
```

## 🚀 Quick Start

### 1. Basic Usage
```python
from commission_reconciliation_system import CommissionReconciliationSystem

# Initialize with default configuration
system = CommissionReconciliationSystem()

# Run full reconciliation
system.run_full_reconciliation()
```

### 2. Run from Command Line
```bash
python commission_reconciliation_system.py
```

### 3. Automated Production Use
```bash
python commission_reconciliation_automation.py
```

## ⚙️ Configuration

### Default Configuration
```python
{
    'landingai_responses_dir': 'landingai_system_responses',
    'enrollment_file': 'docs/enrollment_info.csv',
    'output_dir': 'commission_reconciliation_reports',
    'email_config': {
        'enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': '',
        'sender_password': '',
        'recipients': []
    },
    'supported_carriers': {
        'hne': {
            'name': 'Harvard Pilgrim Health Care',
            'file_pattern': 'HNE_comm_system_response_*.json',
            'table_identifier': 'Incentive ID : Broker Commission'
        }
    }
}
```

### Custom Configuration
```python
custom_config = {
    'landingai_responses_dir': 'landingai_system_responses',
    'enrollment_file': 'docs/enrollment_info.csv',
    'output_dir': 'custom_reports',
    'email_config': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'commissions@company.com',
        'sender_password': 'app-password',
        'recipients': ['manager@company.com', 'finance@company.com']
    },
    'supported_carriers': {
        'hne': {...},
        'aetna': {...},
        'cigna': {...}
    }
}

system = CommissionReconciliationSystem(custom_config)
```

## 🏥 Adding New Carriers

### 1. Add Carrier Configuration
```python
'your_carrier': {
    'name': 'Your Carrier Name',
    'file_pattern': 'YOUR_CARRIER_comm_system_response_*.json',
    'table_identifier': 'Commission Table Header Text'
}
```

### 2. Add Extraction Method
```python
def extract_your_carrier_commission_data(self, json_file: str) -> List[Dict[str, Any]]:
    """Extract commission entries from Your Carrier JSON response."""
    # Implement carrier-specific extraction logic
    pass
```

### 3. Update Processing Logic
In `process_carrier_commissions` method:
```python
elif carrier_code == 'your_carrier':
    commission_entries = self.extract_your_carrier_commission_data(response_file)
```

## 📊 Matching Logic

The system uses **strict matching logic** that requires both:

1. **Member ID (Policy ID)**: Must match exactly between commission statement and enrollment CSV
2. **Effective Date**: Must match exactly (same day) between commission statement and enrollment CSV

### Why Strict Matching?
- Prevents false matches that could lead to incorrect reconciliation
- Ensures accurate financial reporting
- Maintains data integrity across systems
- Follows insurance industry best practices

### Example Matching Process
```python
def find_enrollment_match(self, commission_entry, enrollment_df):
    member_id = commission_entry['member_id']
    commission_date = convert_effective_date(commission_entry['effective_date'])
    
    # Step 1: Find member ID matches
    member_matches = enrollment_df[enrollment_df['policy_id'] == member_id]
    
    # Step 2: From member matches, find exact date match
    for enrollment_record in member_matches:
        if commission_date.date() == enrollment_record['effective_date'].date():
            return enrollment_record  # EXACT MATCH FOUND
    
    return None  # No exact match found
```

## 📧 Email Configuration

### Gmail Setup
1. Enable 2-factor authentication
2. Generate App Password: Google Account Settings > Security > App passwords
3. Use app password in configuration

### Environment Variables (Production)
```bash
export COMMISSION_SENDER_EMAIL='commissions@company.com'
export COMMISSION_SENDER_PASSWORD='your-app-password'
export COMMISSION_RECIPIENTS='manager@company.com,finance@company.com'
```

### Windows Environment Variables
```cmd
set COMMISSION_SENDER_EMAIL=commissions@company.com
set COMMISSION_SENDER_PASSWORD=your-app-password
set COMMISSION_RECIPIENTS=manager@company.com,finance@company.com
```

## 📄 Reports Generated

### 1. Text Reports (`*_commission_report_*.txt`)
- Executive summary with match rates and financial totals
- Detailed matched entries with enrollment cross-reference
- Unmatched entries with reasons
- Reconciliation assessment and recommendations

### 2. JSON Data Files (`*_commission_data_*.json`)
- Complete processed data in structured format
- All extracted commission entries
- Matching results with enrollment details
- Processing metadata and timestamps

### 3. Summary Reports (`commission_reconciliation_summary_*.json`)
- Cross-carrier summary with overall statistics
- Combined financial totals
- System-wide match rates and trends

## 🔄 Automation Setup

### Windows Task Scheduler
1. Create new task
2. Set trigger (daily, weekly, etc.)
3. Set action: Start program `run_commission_reconciliation.bat`
4. Configure failure notifications

### Linux Cron Job
```bash
# Daily at 8 AM
0 8 * * * /path/to/project/commission_reconciliation_automation.py

# Weekly on Monday at 9 AM
0 9 * * 1 /path/to/project/commission_reconciliation_automation.py
```

### Python Scheduler (Alternative)
```python
import schedule
import time

def run_reconciliation():
    system = CommissionReconciliationSystem()
    system.run_full_reconciliation()

schedule.every().day.at("08:00").do(run_reconciliation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🛠️ Maintenance Tasks

### Daily
- Monitor logs for errors or warnings
- Check match rates in email reports
- Verify new response files are being processed

### Weekly
- Review unmatched entries for patterns
- Update enrollment data if needed
- Archive old reports (automated)

### Monthly
- Review and update carrier configurations
- Test email delivery
- Analyze trends in match rates

## 🔍 Troubleshooting

### Common Issues

#### Low Match Rates
**Symptoms**: Match rate below 85%
**Causes**: 
- Missing enrollment records
- Date format mismatches
- Member ID formatting differences
**Solutions**:
- Verify enrollment data completeness
- Check date parsing logic
- Review member ID formats

#### No Files Found
**Symptoms**: "No carrier response files found"
**Causes**:
- Incorrect file patterns
- Files in wrong directory
- File naming convention changes
**Solutions**:
- Check file patterns in configuration
- Verify directory structure
- Update file patterns if needed

#### Email Sending Fails
**Symptoms**: Email-related errors in logs
**Causes**:
- Incorrect SMTP settings
- Authentication failures
- Network/firewall issues
**Solutions**:
- Verify SMTP configuration
- Check app password generation
- Test network connectivity

### Debug Mode
Add debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In your code
logger = logging.getLogger(__name__)
logger.debug(f"Processing {len(entries)} commission entries")
logger.debug(f"Found {len(matches)} member matches for ID {member_id}")
```

## 📈 Performance Considerations

### Optimization Tips
- Use pandas vectorized operations for large datasets
- Implement caching for repeated enrollment lookups
- Consider parallel processing for multiple carriers
- Monitor memory usage with large JSON files

### Scaling
- Partition large enrollment files by carrier
- Implement database storage for historical data
- Use cloud storage for archived reports
- Consider containerization for deployment

## 🔒 Security Considerations

### Email Security
- Use app passwords, not account passwords
- Store credentials in environment variables
- Rotate passwords regularly
- Use encrypted connections (TLS/SSL)

### Data Security
- Ensure PII protection in reports
- Implement access controls for report directories
- Consider encryption for sensitive data files
- Regular security audits of file permissions

## 📚 API Reference

### CommissionReconciliationSystem Class

#### Constructor
```python
CommissionReconciliationSystem(config: Dict[str, Any] = None)
```

#### Main Methods
- `run_full_reconciliation()`: Execute complete reconciliation process
- `process_carrier_commissions(carrier_code, response_files)`: Process specific carrier
- `find_enrollment_match(commission_entry, enrollment_df)`: Find exact match
- `generate_carrier_report(carrier_results)`: Generate text report
- `save_reports(all_results)`: Save all reports to files
- `send_email_report(all_results, report_files)`: Send email with attachments

### Data Structures

#### Commission Entry
```python
{
    'member_id': str,
    'effective_date': str,
    'first_name': str,
    'last_name': str,
    'net_amount': float,
    'carrier': str,
    'source_file': str,
    # ... additional fields
}
```

#### Match Result
```python
{
    'commission_data': Dict,
    'enrollment_data': Dict,
    'match_type': str,
    'match_confidence': str
}
```

## 📞 Support

For issues or questions:
1. Check logs in `logs/commission_reconciliation_*.log`
2. Review configuration in `COMMISSION_RECONCILIATION_CONFIG.md`
3. Run demo script for testing: `python commission_reconciliation_demo.py`
4. Verify file structure and permissions

## 🔄 Version History

### v1.0 (Current)
- Initial release with HNE support
- Strict matching logic implementation
- Email reporting functionality
- Production automation scripts
- Comprehensive documentation

### Future Enhancements
- Database integration for historical tracking
- Web dashboard for monitoring
- Advanced analytics and trend reporting
- Integration with additional LandingAI features