# agents/src/agents/orchestrator.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import asdict

from .email_finder import EmailFinderAgent, EmailSearchResult
from .email_parser import EmailParserAgent, JobApplicationData
from .summarizer import SummarizerAgent
from .excel_writer import ExcelWriterAgent

class JobApplicationOrchestratorAgent:
    """Main orchestrator that coordinates all agents to process job applications."""
    
    def __init__(self, gmail_service, claude_client):
        self.gmail_service = gmail_service
        self.claude_client = claude_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize all agents
        self.email_finder = EmailFinderAgent(gmail_service)
        self.email_parser = EmailParserAgent()
        self.summarizer = SummarizerAgent(claude_client)
        self.excel_writer = ExcelWriterAgent()

    def process_job_applications(self, 
                               start_date: datetime,
                               output_file_path: str,
                               end_date: Optional[datetime] = None,
                               append_mode: bool = False) -> Dict[str, Any]:
        """
        Main workflow to process job applications from Gmail to Excel.
        
        Args:
            start_date: Start date for email search
            output_file_path: Path where Excel file will be created
            end_date: End date for email search (defaults to now)
            append_mode: Whether to append to existing file or overwrite
        
        Returns:
            Dict with processing results and statistics
        """
        results = {
            'success': False,
            'total_emails_found': 0,
            'applications_processed': 0,
            'applications_written': 0,
            'errors': [],
            'output_file': output_file_path
        }
        
        try:
            self.logger.info("Starting job application processing workflow")
            
            # Step 1: Find job-related emails
            self.logger.info("Step 1: Searching for job-related emails...")
            emails = self.email_finder.search_job_emails(start_date, end_date)
            results['total_emails_found'] = len(emails)
            
            if not emails:
                self.logger.warning("No job-related emails found")
                results['errors'].append("No job-related emails found in the specified date range")
                return results
            
            self.logger.info(f"Found {len(emails)} job-related emails")
            
            # Step 2: Parse emails and extract job data
            self.logger.info("Step 2: Parsing email content...")
            job_applications = []
            
            for i, email in enumerate(emails):
                try:
                    self.logger.info(f"Processing email {i+1}/{len(emails)}: {email.subject[:50]}...")
                    
                    # Parse email content
                    job_data = self.email_parser.parse_email(email)
                    
                    # Generate summary
                    summary = self.summarizer.summarize_email(job_data)
                    
                    # Convert to dict and add summary
                    job_dict = asdict(job_data)
                    job_dict['summary'] = summary
                    
                    job_applications.append(job_dict)
                    results['applications_processed'] += 1
                    
                except Exception as e:
                    error_msg = f"Error processing email {i+1}: {e}"
                    self.logger.error(error_msg)
                    results['errors'].append(error_msg)
                    continue
            
            if not job_applications:
                self.logger.error("No applications could be processed")
                results['errors'].append("Failed to process any job applications")
                return results
            
            # Step 3: Write to Excel
            self.logger.info(f"Step 3: Writing {len(job_applications)} applications to Excel...")
            
            if append_mode:
                write_success = self.excel_writer.append_to_excel(job_applications, output_file_path)
            else:
                write_success = self.excel_writer.write_to_excel(
                    job_applications, 
                    output_file_path, 
                    overwrite=True
                )
            
            if write_success:
                results['applications_written'] = len(job_applications)
                results['success'] = True
                self.logger.info(f"Successfully completed processing. Output file: {output_file_path}")
            else:
                results['errors'].append("Failed to write Excel file")
                self.logger.error("Failed to write Excel file")
            
        except Exception as e:
            error_msg = f"Critical error in orchestrator: {e}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results

    def get_processing_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of processing results."""
        if results['success']:
            summary = f"""
✅ Job Application Processing Completed Successfully!

📊 Summary:
- Emails searched: {results['total_emails_found']} job-related emails found
- Applications processed: {results['applications_processed']}
- Applications written to Excel: {results['applications_written']}
- Output file: {results['output_file']}

🎉 Your job application tracker has been updated!
"""
        else:
            summary = f"""
❌ Job Application Processing Failed

📊 Summary:
- Emails found: {results['total_emails_found']}
- Applications processed: {results['applications_processed']}
- Applications written: {results['applications_written']}

🚨 Errors encountered:
"""
            for error in results['errors']:
                summary += f"- {error}\n"
        
        return summary
