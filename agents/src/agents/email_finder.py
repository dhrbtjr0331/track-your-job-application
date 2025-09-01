# agents/src/agents/email_finder.py
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class EmailSearchResult:
    message_id: str
    thread_id: str
    subject: str
    sender: str
    date: datetime
    snippet: str
    body: str

class EmailFinderAgent:
    """Agent responsible for finding job application related emails from Gmail."""
    
    def __init__(self, gmail_service):
        self.gmail_service = gmail_service
        self.logger = logging.getLogger(__name__)
        
        # Keywords that indicate job application emails
        self.job_keywords = [
            'application', 'interview', 'position', 'role', 'job',
            'internship', 'hiring', 'recruit', 'candidate', 'resume',
            'cv', 'opportunity', 'opening', 'career', 'thank you for applying',
            'application received', 'application status', 'next steps',
            'phone screen', 'technical interview', 'final round',
            'offer', 'rejection', 'unfortunately', 'congratulations'
        ]
        
        # Common job application domains
        self.job_domains = [
            'greenhouse.io', 'lever.co', 'workable.com', 'bamboohr.com',
            'ashbyhq.com', 'eightfold.ai', 'icims.com', 'smartrecruiters.com',
            'workday.com', 'successfactors.com', 'taleo.net', 'breezy.hr',
            'recruitee.com', 'jobvite.com', 'indeed.com', 'linkedin.com',
            'glassdoor.com', 'angel.co', 'workatastartup.com'
        ]

    def search_job_emails(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[EmailSearchResult]:
        """Search for job application related emails within date range."""
        try:
            if end_date is None:
                end_date = datetime.now()
            
            # Build Gmail search query
            query_parts = []
            
            # Date range
            query_parts.append(f"after:{start_date.strftime('%Y/%m/%d')}")
            query_parts.append(f"before:{end_date.strftime('%Y/%m/%d')}")
            
            # Keywords (using OR)
            keyword_query = " OR ".join([f'"{keyword}"' for keyword in self.job_keywords[:10]])  # Limit for query length
            query_parts.append(f"({keyword_query})")
            
            # Domain filter (using OR)
            domain_query = " OR ".join([f"from:{domain}" for domain in self.job_domains[:5]])  # Limit for query length
            query_parts.append(f"({domain_query})")
            
            # Combine with OR between keyword and domain filters
            final_query = f"{query_parts[0]} {query_parts[1]} ({query_parts[2]} OR {query_parts[3]})"
            
            self.logger.info(f"Gmail search query: {final_query}")
            
            # Execute search using Gmail service
            results = self.gmail_service.search_messages(final_query)
            
            job_emails = []
            for message in results:
                try:
                    # Get full message content
                    thread_content = self.gmail_service.read_thread(message['threadId'])
                    
                    email_result = EmailSearchResult(
                        message_id=message['id'],
                        thread_id=message['threadId'],
                        subject=self._extract_subject(thread_content),
                        sender=self._extract_sender(thread_content),
                        date=self._extract_date(thread_content),
                        snippet=message.get('snippet', ''),
                        body=self._extract_body(thread_content)
                    )
                    
                    if self._is_job_related(email_result):
                        job_emails.append(email_result)
                        
                except Exception as e:
                    self.logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            self.logger.info(f"Found {len(job_emails)} job-related emails")
            return job_emails
            
        except Exception as e:
            self.logger.error(f"Error searching emails: {e}")
            return []

    def _extract_subject(self, thread_content) -> str:
        """Extract subject from thread content."""
        # Implementation depends on Gmail service structure
        if 'messages' in thread_content and thread_content['messages']:
            for message in thread_content['messages']:
                if 'payload' in message and 'headers' in message['payload']:
                    for header in message['payload']['headers']:
                        if header['name'].lower() == 'subject':
                            return header['value']
        return ""

    def _extract_sender(self, thread_content) -> str:
        """Extract sender from thread content."""
        if 'messages' in thread_content and thread_content['messages']:
            for message in thread_content['messages']:
                if 'payload' in message and 'headers' in message['payload']:
                    for header in message['payload']['headers']:
                        if header['name'].lower() == 'from':
                            return header['value']
        return ""

    def _extract_date(self, thread_content) -> datetime:
        """Extract date from thread content."""
        if 'messages' in thread_content and thread_content['messages']:
            for message in thread_content['messages']:
                if 'internalDate' in message:
                    timestamp = int(message['internalDate']) / 1000
                    return datetime.fromtimestamp(timestamp)
        return datetime.now()

    def _extract_body(self, thread_content) -> str:
        """Extract email body from thread content."""
        full_body = ""
        if 'messages' in thread_content and thread_content['messages']:
            for message in thread_content['messages']:
                body_parts = self._extract_message_body(message)
                full_body += body_parts + "\n\n"
        return full_body.strip()

    def _extract_message_body(self, message) -> str:
        """Extract body from individual message."""
        body = ""
        if 'payload' in message:
            body = self._extract_body_from_payload(message['payload'])
        return body

    def _extract_body_from_payload(self, payload) -> str:
        """Recursively extract body from message payload."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                body += self._extract_body_from_payload(part)
        else:
            if 'body' in payload and 'data' in payload['body']:
                import base64
                data = payload['body']['data']
                data = data.replace('-', '+').replace('_', '/')
                decoded = base64.b64decode(data).decode('utf-8', errors='ignore')
                body += decoded
        
        return body

    def _is_job_related(self, email: EmailSearchResult) -> bool:
        """Determine if email is actually job application related."""
        text_to_check = f"{email.subject} {email.body} {email.sender}".lower()
        
        # Check for job-related keywords
        keyword_matches = sum(1 for keyword in self.job_keywords if keyword in text_to_check)
        
        # Check for job domains
        domain_matches = sum(1 for domain in self.job_domains if domain in email.sender.lower())
        
        # Heuristic: needs at least 1 keyword match OR domain match
        return keyword_matches >= 1 or domain_matches >= 1

