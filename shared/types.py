from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    UNDER_REVIEW = "Under Review"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEW_COMPLETE = "Interview Complete"
    OFFER = "Offer"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"
    ACCEPTED = "Accepted"

class ProcessingStage(str, Enum):
    INITIALIZING = "initializing"
    FINDING_EMAILS = "finding_emails"
    PARSING_EMAILS = "parsing_emails"
    SUMMARIZING = "summarizing"
    TRACKING_STATUS = "tracking_status"
    WRITING_EXCEL = "writing_excel"
    COMPLETED = "completed"
    ERROR = "error"

class Application(BaseModel):
    id: str
    company: str
    position: str
    applied_date: str
    status: ApplicationStatus
    source: str
    location: Optional[str] = None
    job_id: Optional[str] = None
    status_link: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ApplicationInput(BaseModel):
    company: str
    position: str
    applied_date: str
    status: ApplicationStatus
    source: str
    location: Optional[str] = None
    job_id: Optional[str] = None
    status_link: Optional[str] = None
    notes: Optional[str] = None

class ProcessingRequest(BaseModel):
    start_date: str
    end_date: Optional[str] = None
    output_path: str
    overwrite_existing: bool = False

class ProcessingResult(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    applications_found: int
    applications_processed: int
    errors: Optional[List[str]] = None

class ProcessingUpdate(BaseModel):
    stage: ProcessingStage
    progress: int  # 0-100
    message: str
    current_agent: Optional[str] = None
    error: Optional[str] = None

class EmailData(BaseModel):
    id: str
    subject: str
    sender: str
    recipient: str
    date: str
    body: str
    snippet: str
    labels: List[str]

class AgentResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float

class EmailFinderResponse(BaseModel):
    emails: List[EmailData]
    total_found: int
    relevance_scores: List[float]

class EmailParserResponse(BaseModel):
    applications: List[Dict[str, Any]]
    confidence: float
    extracted_fields: List[str]

class SummarizerResponse(BaseModel):
    summary: str
    word_count: int
    key_points: List[str]

class StatusTrackerResponse(BaseModel):
    status: ApplicationStatus
    confidence: float
    reasoning: str

class ExcelWriterConfig(BaseModel):
    file_path: str
    overwrite: bool = False
    include_headers: bool = True
    formatting: Dict[str, Any] = {
        "date_format": "YYYY-MM-DD",
        "column_widths": {
            "Company": 25,
            "Position": 60,
            "Applied Date": 12,
            "Status": 18,
            "Source": 20,
            "Location": 15,
            "Job ID": 15,
            "Status Link": 50,
            "Notes": 50
        },
        "freeze_first_row": True
    }
