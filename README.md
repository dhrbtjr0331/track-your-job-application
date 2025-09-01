# Job Application Tracker

A multi-agent AI system that automatically tracks job applications by analyzing Gmail emails and generating structured Excel reports.

## Features

- 🔍 **Smart Email Detection**: Automatically finds job application emails from Gmail
- 📊 **Excel Generation**: Creates structured spreadsheets with application data
- 🤖 **AI-Powered Analysis**: Uses Claude AI for email parsing and summarization
- 🔄 **Real-time Updates**: WebSocket-based progress tracking
- 📅 **Flexible Date Ranges**: User-defined search periods
- 📁 **Custom File Paths**: Choose where to save your Excel files

## Architecture

- **Frontend**: React + TypeScript + TailwindCSS
- **Backend**: Go + GraphQL + WebSocket + Gmail API
- **Agents**: Python + LangGraph + Anthropic Claude API
- **Database**: PostgreSQL + Redis

## Multi-Agent System

1. **Email Finder**: Searches Gmail for job-related emails
2. **Email Parser**: Extracts structured data from emails
3. **Summarizer**: Creates concise 30-word summaries
4. **Status Tracker**: Determines application status
5. **Excel Writer**: Generates formatted Excel files

## Getting Started

### Prerequisites

- Go 1.21+
- Python 3.9+
- Node.js 18+
- PostgreSQL
- Redis

### Environment Setup

1. Clone the repository
2. Set up environment variables (see `.env.example`)
3. Install dependencies for all components
4. Run database migrations
5. Start the development servers

### API Keys Required

- Google Gmail API credentials
- Anthropic Claude API key

## Development

```bash
# Start all services
docker-compose up -d

# Frontend development
cd frontend && npm run dev

# Backend development
cd backend && go run main.go

# Agents development
cd agents && python main.py
```

## License

MIT License
