# 📊 Job Application Tracker

An intelligent multi-agent system that automatically tracks your job applications by analyzing Gmail emails and generating organized Excel spreadsheets.

## 🎯 Features

- **📧 Smart Email Detection**: Automatically finds job application related emails
- **🔍 Intelligent Parsing**: Extracts company, position, date, status, and more
- **🤖 AI-Powered Summaries**: Uses Claude to generate concise 30-word summaries
- **📊 Excel Export**: Creates perfectly formatted Excel files with all application data
- **🔄 Incremental Updates**: Append new applications to existing spreadsheets
- **🚀 Multi-Agent Architecture**: Specialized agents for each task

## 🏗️ Architecture

### Multi-Agent System
1. **📧 Email Finder Agent** - Searches Gmail for job-related emails
2. **📝 Email Parser Agent** - Extracts structured data from emails  
3. **✍️ Summarizer Agent** - Creates AI-powered summaries using Claude
4. **📊 Excel Writer Agent** - Generates formatted Excel files
5. **🎯 Orchestrator Agent** - Coordinates the entire workflow

### Technology Stack
- **Agents**: Python + FastAPI + LangGraph + Anthropic Claude
- **Backend**: Go + GraphQL + WebSocket (future)
- **Frontend**: React + TypeScript + TailwindCSS (future)
- **Database**: PostgreSQL + Redis

## 🚀 Quick Start

### 1. Setup
```bash
# Clone and setup
git clone <repository>
cd job-application-tracker
chmod +x setup-dev.sh
./setup-dev.sh
```

### 2. Configure Environment
```bash
# Edit .env file
cp .env.example .env
# Add your Anthropic API key and Gmail credentials
```

### 3. Run the Agents
```bash
# Start the agents service
make agents-dev
# or
cd agents && python main.py
```

### 4. Process Applications
```bash
# API call example
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-08-01",
    "output_file_path": "./outputs/my_applications.xlsx",
    "append_mode": false
  }'
```

## 📊 Excel Output Format

The system generates Excel files with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Company | Company name | "CreativeMode" |
| Position | Job title | "SWE Intern (Summer 2026)" |
| Applied Date | Date (YYYY-MM-DD) | "2025-08-23" |
| Status | Application status | "Applied" |
| Source | Application platform | "Y Combinator" |
| Location | Job location | "San Francisco, CA" |
| Job ID | Unique identifier | "dc9d2442-..." |
| Status Link | Application URL | "https://..." |
| Notes | AI-generated summary (≤30 words) | "YC startup application..." |

## 🔧 API Endpoints

### `POST /process`
Main processing endpoint that converts Gmail emails to Excel.

**Request:**
```json
{
  "start_date": "2025-08-01",
  "output_file_path": "./outputs/applications.xlsx",  
  "end_date": "2025-09-01",
  "append_mode": false
}
```

**Response:**
```json
{
  "success": true,
  "total_emails_found": 25,
  "applications_processed": 23,
  "applications_written": 23,
  "errors": [],
  "output_file": "./outputs/applications.xlsx",
  "summary": "✅ Processing completed successfully!"
}
```

### `GET /health`
Health check endpoint.

## 🛠️ Development

### Available Commands
```bash
make help          # Show all commands
make setup         # Complete setup
make start         # Start all services  
make stop          # Stop services
make logs          # View logs
make agents-dev    # Run agents in dev mode
make test          # Run tests
make lint          # Run linters
make clean         # Clean up
```

### Project Structure
```
job-application-tracker/
├── agents/                    # Python Multi-Agent System
│   ├── src/agents/           # Individual agent implementations
│   ├── src/services/         # Gmail and Claude services
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── backend/                  # Go Backend (future)
├── frontend/                # React Frontend (future)
├── outputs/                 # Generated Excel files
├── credentials/             # API credentials
└── docker-compose.yml       # Service orchestration
```

## 🔐 Setup Requirements

### 1. Anthropic API Key
- Get your Claude API key from [Anthropic Console](https://console.anthropic.com/)
- Add to `.env` as `ANTHROPIC_API_KEY`

### 2. Gmail API Access  
- Create project in [Google Cloud Console](https://console.cloud.google.com/)
- Enable Gmail API
- Create OAuth 2.0 credentials
- Download and save as `credentials/gmail_credentials.json`

## 🧪 Testing

The system can be tested with your actual Gmail data:

```bash
# Test with recent emails
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  