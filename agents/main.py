import os
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from src.services.orchestrator import AgentOrchestrator
from src.services.gmail_service import GmailService
from src.services.database_service import DatabaseService
from shared.types import ProcessingRequest, ProcessingResult

# Load environment variables
load_dotenv()

# Global services
orchestrator = None
gmail_service = None
db_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global orchestrator, gmail_service, db_service
    
    # Initialize services
    gmail_service = GmailService()
    db_service = DatabaseService()
    orchestrator = AgentOrchestrator(gmail_service, db_service)
    
    print("🤖 Agent services initialized successfully")
    yield
    
    # Shutdown
    await db_service.close()
    print("🔄 Agent services shut down")

# Create FastAPI app
app = FastAPI(
    title="Job Application Tracker - Agents",
    description="Multi-agent system for processing job application emails",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "job-application-tracker-agents",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check if services are initialized
        if not all([orchestrator, gmail_service, db_service]):
            return {"status": "unhealthy", "message": "Services not initialized"}
        
        # Test database connection
        await db_service.test_connection()
        
        return {
            "status": "healthy",
            "services": {
                "orchestrator": "ready",
                "gmail_service": "ready",
                "database": "connected"
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/process", response_model=ProcessingResult)
async def process_applications(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks
):
    """
    Start processing job applications from Gmail emails
    """
    try:
        # Validate request
        if not request.start_date:
            raise HTTPException(status_code=400, detail="Start date is required")
        
        if not request.output_path:
            raise HTTPException(status_code=400, detail="Output path is required")
        
        # Start processing in background
        background_tasks.add_task(
            orchestrator.process_applications,
            request
        )
        
        return ProcessingResult(
            success=True,
            message="Processing started successfully",
            applications_found=0,  # Will be updated during processing
            applications_processed=0,
            file_path=request.output_path
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_available_agents():
    """Get list of available agents and their status"""
    try:
        return {
            "agents": [
                {
                    "name": "EmailFinder",
                    "description": "Finds job application emails from Gmail",
                    "status": "ready"
                },
                {
                    "name": "EmailParser", 
                    "description": "Extracts structured data from emails",
                    "status": "ready"
                },
                {
                    "name": "Summarizer",
                    "description": "Creates concise email summaries",
                    "status": "ready"
                },
                {
                    "name": "StatusTracker",
                    "description": "Determines application status",
                    "status": "ready"
                },
                {
                    "name": "ExcelWriter",
                    "description": "Generates Excel files",
                    "status": "ready"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-agent/{agent_name}")
async def test_agent(agent_name: str, test_data: dict = None):
    """Test individual agent functionality"""
    try:
        if agent_name not in ["email_finder", "email_parser", "summarizer", "status_tracker", "excel_writer"]:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        result = await orchestrator.test_agent(agent_name, test_data or {})
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/processing-status/{job_id}")
async def get_processing_status(job_id: str):
    """Get processing status for a job"""
    try:
        status = await orchestrator.get_processing_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("AGENTS_PORT", "8000")),
        reload=True,
        log_level="info"
    )
