// Application represents a job application entry
export interface Application {
  id: string;
  company: string;
  position: string;
  appliedDate: string; // ISO date string
  status: ApplicationStatus;
  source: string;
  location?: string;
  jobId?: string;
  statusLink?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

// ApplicationInput for creating/updating applications
export interface ApplicationInput {
  company: string;
  position: string;
  appliedDate: string;
  status: ApplicationStatus;
  source: string;
  location?: string;
  jobId?: string;
  statusLink?: string;
  notes?: string;
}

// Application status enum
export enum ApplicationStatus {
  APPLIED = "Applied",
  UNDER_REVIEW = "Under Review",
  INTERVIEW_SCHEDULED = "Interview Scheduled",
  INTERVIEW_COMPLETE = "Interview Complete",
  OFFER = "Offer",
  REJECTED = "Rejected",
  WITHDRAWN = "Withdrawn",
  ACCEPTED = "Accepted"
}

// Processing request
export interface ProcessingRequest {
  startDate: string; // ISO date string
  endDate?: string; // ISO date string, defaults to now
  outputPath: string;
  overwriteExisting: boolean;
}

// Processing result
export interface ProcessingResult {
  success: boolean;
  message: string;
  filePath?: string;
  applicationsFound: number;
  applicationsProcessed: number;
  errors?: string[];
}

// Processing status update for WebSocket
export interface ProcessingUpdate {
  stage: ProcessingStage;
  progress: number; // 0-100
  message: string;
  currentAgent?: string;
  error?: string;
}

export enum ProcessingStage {
  INITIALIZING = "initializing",
  FINDING_EMAILS = "finding_emails",
  PARSING_EMAILS = "parsing_emails",
  SUMMARIZING = "summarizing",
  TRACKING_STATUS = "tracking_status",
  WRITING_EXCEL = "writing_excel",
  COMPLETED = "completed",
  ERROR = "error"
}

// Email data for agents
export interface EmailData {
  id: string;
  subject: string;
  from: string;
  to: string;
  date: string;
  body: string;
  snippet: string;
  labels: string[];
}

// Agent response types
export interface AgentResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  processingTime: number;
}

export interface EmailFinderResponse {
  emails: EmailData[];
  totalFound: number;
  relevanceScores: number[];
}

export interface EmailParserResponse {
  applications: Partial<Application>[];
  confidence: number;
  extractedFields: string[];
}

export interface SummarizerResponse {
  summary: string;
  wordCount: number;
  keyPoints: string[];
}

export interface StatusTrackerResponse {
  status: ApplicationStatus;
  confidence: number;
  reasoning: string;
}

// Excel writer configuration
export interface ExcelWriterConfig {
  filePath: string;
  overwrite: boolean;
  includeHeaders: boolean;
  formatting: {
    dateFormat: string;
    columnWidths: Record<string, number>;
    freezeFirstRow: boolean;
  };
}
