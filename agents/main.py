# agents/main.py
import os
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.agents.orchestrator import JobApplicationOrchestratorAgent
from src.services.gmail_service import GmailService
from src.services.claude_service import ClaudeService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Job Application Tracker Agents", version="1.0.0")

# Request models
class ProcessJobApplicationsRequest(BaseModel):
    start_date: str  # Format: YYYY-MM-DD
    output_file_path: str
    end_date: Optional[str] = None
    append_mode: bool = False

class ProcessingResponse(BaseModel):
    success: bool
    total_emails_found: int
    applications_processed: int
    applications_written: int
    errors: list
    output_file: str
    summary: str

# Global services (will be initialized on startup)
gmail_service = None
claude_service = None
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global gmail_service, claude_service, orchestrator
    
    try:
        # Initialize Claude service
        claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        claude_service = ClaudeService(claude_api_key)
        logger.info("Claude service initialized")
        
        # Gmail service will be initialized when first used
        # (since it requires MCP tools to be available)
        
        logger.info("Services initialization completed")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "claude": claude_service is not None,
            "gmail": gmail_service is not None
        }
    }

@app.post("/process", response_model=ProcessingResponse)
async def process_job_applications(request: ProcessJobApplicationsRequest):
    """Main endpoint to process job applications from Gmail to Excel."""
    global gmail_service, orchestrator
    
    try:
        # Initialize Gmail service if not already done
        if gmail_service is None:
            # This would need to be connected to actual MCP tools
            # For now, this is a placeholder
            gmail_service = GmailService(None)  # TODO: Connect to actual MCP tools
        
        # Initialize orchestrator if not already done
        if orchestrator is None:
            orchestrator = JobApplicationOrchestratorAgent(gmail_service, claude_service)
        
        # Parse dates
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = None
        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        # Process job applications
        results = orchestrator.process_job_applications(
            start_date=start_date,
            output_file_path=request.output_file_path,
            end_date=end_date,
            append_mode=request.append_mode
        )
        
        # Generate summary
        summary = orchestrator.get_processing_summary(results)
        
        return ProcessingResponse(
            success=results['success'],
            total_emails_found=results['total_emails_found'],
            applications_processed=results['applications_processed'],
            applications_written=results['applications_written'],
            errors=results['errors'],
            output_file=results['output_file'],
            summary=summary
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Error processing job applications: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Job Application Tracker Agents API",
        "version": "1.0.0",
        "endpoints": {
            "process": "/process - Main processing endpoint",
            "health": "/health - Health check",
            "docs": "/docs - API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
