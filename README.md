# CompiSure AI Commission Reconciliation System

🤖 **Production-Ready AI-Powered Commission Statement Processing & Reconciliation**

An intelligent automation system that processes commission statements from multiple carriers, extracts data using AI/LLM technology, performs reconciliation analysis, and delivers comprehensive reports.

## 🚀 System Overview

### Core Features
- **🧠 Multi-Carrier Support**: HC, HNE, Humana with extensible pattern extraction
- **🔍 Hybrid Extraction**: Pattern-based extraction with LLM fallback for reliability
- **📊 Automated Reconciliation**: Policy mapping and variance analysis
- **📧 Email Integration**: Automated report distribution 
- **🔒 PHI Compliance**: Built-in data scrubbing for privacy protection
- **📈 Multi-format Reports**: Excel, HTML, PDF with visualizations

### Supported Carriers
- **Health Choice (HC)** - Pattern-based extraction
- **Harvard Pilgrim Health Care Northeast (HNE)** - Individual amount mapping
- **Humana** - Name-to-policy ID conversion
- *Extensible architecture for additional carriers*

## 🏗️ Architecture

```
CompiSure_AI_Agents/
├── 📁 src/                           # Core application modules
│   ├── commission_processor.py       # Main processing orchestration
│   ├── reconciliation_engine.py      # Policy mapping & variance analysis
│   ├── llm_extraction_service.py     # AI-powered data extraction
│   ├── report_generator.py           # Multi-format report generation
│   ├── email_service.py              # Email distribution system
│   ├── phi_scrubber.py               # Privacy compliance
│   ├── pattern_extractors/           # Carrier-specific extractors
│   │   └── hc_extractor.py           # Health Choice patterns
│   └── utils.py                      # Shared utilities
├── 📁 config/                        # Configuration files
├── 📁 docs/                          # Commission statements & documentation
├── 📁 logs/                          # System operation logs (auto-created)
├── 📁 reports/                       # Generated reports (auto-created)
├── 🐍 main.py                        # Primary application entry point
├── 🤖 monitor_commissions.py         # File monitoring service
└── 📝 requirements.txt               # Python dependencies
```

## 🏃‍♂️ Quick Start

### Prerequisites
- **Python 3.8+**
- **OpenAI API Key**
- **Gmail Account with App Password**

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/karthik2sekhar/CompiSure_Agents.git
cd CompiSure_Agents
```

2. **Create virtual environment**:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install watchdog python-dotenv openai pandas openpyxl reportlab matplotlib seaborn PyPDF2 smtplib-ssl
```

4. **Configure environment** (one-time setup):
```bash
python setup_email.py
```
   - Enter your Gmail credentials
   - Provide OpenAI API key
   - Set email recipients

### Usage

#### Automatic Monitoring Mode (Recommended)
```bash
python monitor_commissions.py
```
- **Real-time monitoring** of the `docs` folder
- **Automatic processing** of new commission statements
- **Instant email reports** upon file detection

#### Manual Processing Mode
```bash
python main.py
```
- **On-demand processing** of all files in `docs` folder
## 🔧 Configuration

### Environment Variables (.env)
```env
# Email Configuration
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your_app_password
EMAIL_RECIPIENTS=recipient1@email.com,recipient2@email.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Email Setup
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Google Account → Security → 2-Step Verification → App Passwords
3. Use the app password (not your regular Gmail password)

## 📊 Sample Reports

### Reconciliation Summary
- **Total Commissions**: Cross-carrier commission totals
- **Variance Analysis**: Expected vs Actual comparisons
- **Policy-level Details**: Individual policy reconciliation
- **Visual Analytics**: Charts and graphs for quick insights

### Report Formats
- **📊 Excel**: Detailed data with multiple worksheets
- **🌐 HTML**: Interactive web-based reports
- **📄 PDF**: Executive summary with key metrics
- **🔗 JSON**: Raw data for API integration
- **📈 Charts**: Commission distribution and variance analysis

## 🤖 AI Integration

### OpenAI GPT-3.5 Features
- **Intelligent PDF Parsing**: Extracts structured data from complex PDF layouts
- **Context-Aware Processing**: Understands insurance industry terminology
- **Error Handling**: Graceful fallback to regex patterns when needed
- **Cost Optimization**: ~$0.0014 per document processing

## 🔍 Monitoring & Logging

### Real-time Monitoring
- **File System Events**: Detects file additions instantly
- **Processing Status**: Live feedback on extraction progress
- **Error Handling**: Comprehensive error logging and recovery

### Logging Levels
- **INFO**: Normal operations and status updates
- **WARNING**: Non-critical issues (missing enrollment data)
- **ERROR**: Processing failures and system errors

## 🚀 Deployment Options

### Local Development
- Run directly from command line
- Suitable for testing and development

### Production Deployment
- **Windows Service**: Use `nssm` or similar tools
- **Linux Daemon**: Systemd service configuration
- **Docker Container**: Containerized deployment (coming soon)

## 🔒 Security Considerations

- **Environment Variables**: Sensitive data stored in `.env` files
- **Git Exclusion**: `.env` files automatically excluded from version control
- **API Key Management**: Secure OpenAI API key handling
- **Email Security**: App passwords instead of primary credentials

## 📈 Performance Metrics

- **File Detection**: ~1-2 seconds after file creation
- **AI Processing**: ~3-5 seconds per PDF document
- **Report Generation**: ~2-3 seconds for all formats
- **Email Delivery**: ~1-2 seconds via Gmail SMTP

## 🛠️ Troubleshooting

### Common Issues

**No emails received**:
- Verify Gmail app password setup
- Check email configuration in `.env`
- Review logs for SMTP errors

**AI extraction showing $0 values**:
- Confirm OpenAI API key is valid
- Check API usage limits
- Verify PDF file quality

**File monitoring not working**:
- Ensure virtual environment is activated
- Check file permissions on `docs` folder
- Verify `watchdog` package installation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **GitHub Issues**: [Create an issue](https://github.com/karthik2sekhar/CompiSure_Agents/issues)
- **Documentation**: Check this README and code comments
- **Logs**: Review `logs/` folder for detailed error information

---

**Made with ❤️ for Insurance Professionals**

*Automate your commission reconciliation process with AI-powered intelligence!*