# Production Deployment Guide

## Quick Start

1. **Clone and Setup**
```bash
git clone https://github.com/karthik2sekhar/CompiSure_Agents.git
cd CompiSure_Agents
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Run**
```bash
# One-time processing
python main.py

# Continuous monitoring
python monitor_commissions.py
```

## Docker Deployment

```bash
# Build and run
docker-compose up -d

# One-time processing
docker-compose run --rm commission-processor
```

## Directory Structure

```
├── src/                     # Core application code
├── config/                  # Configuration files
├── docs/                    # Input documents (PDFs, CSV)
├── logs/                    # Application logs
├── reports/                 # Generated reports
├── main.py                  # One-time processing entry point
├── monitor_commissions.py   # Continuous monitoring entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── docker-compose.yml      # Multi-container setup
```

## Environment Variables

Required variables in `.env`:
- `OPENAI_API_KEY`: OpenAI API key for AI processing
- `SMTP_SERVER`: Email server (e.g., smtp.gmail.com)
- `EMAIL_ADDRESS`: Sender email address
- `EMAIL_PASSWORD`: Email password/app password
- `RECIPIENT_EMAIL`: Report recipient email

## Production Considerations

1. **Security**: Use app passwords, not account passwords
2. **Monitoring**: Check logs/ directory for errors
3. **Backup**: Regular backup of config/ and docs/ directories
4. **Scaling**: Use Docker for consistent deployments
5. **Updates**: Regular dependency updates for security