# Commission Reconciliation System

An automated system for processing health insurance commission statements, performing variance analysis, and generating comprehensive reports.

## Features

- **Multi-Carrier Support**: Processes commission statements from HC, HNE, Humana, and other carriers
- **AI-Powered Extraction**: Uses OpenAI GPT models for accurate data extraction from PDFs
- **Automated Reconciliation**: Compares actual vs expected commissions with configurable tolerance
- **Comprehensive Reporting**: Generates PDF, HTML, Excel reports and visualizations
- **Email Notifications**: Sends automated email reports with variance analysis
- **File Monitoring**: Continuously monitors for new commission statements
- **Period-Specific Processing**: Handles commission statements for different time periods

## Requirements

- Python 3.8+
- OpenAI API key
- Email account with SMTP access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/karthik2sekhar/CompiSure_Agents.git
cd CompiSure_Agents
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

### Environment Variables (.env)

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com

# Processing Configuration
VARIANCE_TOLERANCE=5.0
LOG_LEVEL=INFO
```

### Directory Structure

```
docs/                    # Place commission PDFs here
├── enrollment_info.csv  # Member enrollment data
config/
├── learned_formats.json # AI learning data
logs/                    # Application logs
reports/                 # Generated reports
src/                     # Source code
```

## Usage

### One-time Processing

Run the main workflow to process all commission statements in the `docs/` folder:

```bash
python main.py
```

### Continuous Monitoring

Start the file monitor to automatically process new commission statements:

```bash
python monitor_commissions.py
```

Or use the batch file on Windows:
```bash
start_monitor.bat
```

## Input Files

### Commission Statements
Place PDF commission statements in the `docs/` folder. Supported formats:
- HC commission statements
- HNE commission statements  
- Humana commission statements
- Other carrier formats (processed via AI)

### Enrollment Data
Update `docs/enrollment_info.csv` with current member enrollment information:

```csv
policy_id,member_name,employer_name,carrier,statement_date,expected_commission
771140,John Doe,ABC Company,hc,2025-07-01,300.00
```

## Output Reports

The system generates multiple report formats:

1. **PDF Executive Summary**: High-level variance analysis
2. **HTML Report**: Detailed interactive report
3. **Excel Workbook**: Raw data with multiple sheets
4. **Email Notifications**: Automated summaries
5. **Visualizations**: Charts and graphs

## System Architecture

### Core Components

- **CommissionProcessor**: Extracts data from PDF statements
- **ReconciliationEngine**: Performs variance analysis
- **ReportGenerator**: Creates reports in multiple formats
- **EmailService**: Sends automated notifications
- **LLMExtractionService**: AI-powered data extraction
- **FileMonitor**: Watches for new files

### Data Flow

1. Commission PDFs placed in `docs/` folder
2. AI extracts commission data and identifies statement dates
3. System matches extracted data with enrollment records
4. Variance analysis compares actual vs expected commissions
5. Reports generated and emailed to stakeholders

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "monitor_commissions.py"]
```

### Environment Setup

- Use environment variables for all configuration
- Set up proper logging and monitoring
- Configure secure SMTP settings
- Implement proper error handling and alerting

### Scheduling

For scheduled runs, use cron (Linux/Mac) or Task Scheduler (Windows):

```bash
# Run every weekday at 9 AM
0 9 * * 1-5 /path/to/python /path/to/main.py
```

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Check API key and billing status
2. **Email Failures**: Verify SMTP settings and app passwords
3. **PDF Processing Errors**: Ensure PDFs are readable and not password-protected
4. **Missing Data**: Check enrollment_info.csv format and completeness

### Logs

Check the `logs/` directory for detailed execution logs:
- Application logs include processing details
- Error logs contain exception information
- Email logs track delivery status

## Support

For issues and questions:
1. Check the logs directory for error details
2. Verify configuration in .env file
3. Ensure all required files are in docs/ folder
4. Review email setup guide in EMAIL_SETUP_GUIDE.md