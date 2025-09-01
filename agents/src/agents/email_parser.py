# agents/src/agents/email_parser.py
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

@dataclass
class JobApplicationData:
    company: str
    position: str
    applied_date: str  # YYYY-MM-DD format
    status: str
    source: str
    location: str
    job_id: str
    status_link: str
    email_content: str  # For summarization

class EmailParserAgent:
    """Agent responsible for parsing job application data from emails."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Regex patterns for extracting information
        self.company_patterns = [
            r"from (.+?)@(.+?)\.",  # From email domain
            r"(?:at|@|with) ([A-Z][a-zA-Z\s&.,-]+?)(?:\s|$|\.)",  # "at Company Name"
            r"([A-Z][a-zA-Z\s&.,-]{2,30}) (?:team|hiring|recruitment|talent)",  # "Company hiring"
        ]
        
        self.position_patterns = [
            r"(?:position|role|job|opening)(?:\s+for)?(?:\s+the)?:?\s+([^\n\r.!?]{5,100})",
            r"applied for(?:\s+the)?\s+([^\n\r.!?]{5,100})\s+(?:position|role)",
            r"(?:software engineer|developer|intern|analyst|manager)[^\n\r.!?]{0,50}",
            r"title:\s*([^\n\r.!?]{5,100})",
        ]
        
        self.status_patterns = [
            r"(?:status|application)(?:\s+is)?:?\s+(approved|rejected|pending|under review|interviewed|hired|declined)",
            r"unfortunately|regret|sorry.*inform",  # Rejection indicators
            r"congratulations|pleased.*inform|happy.*inform|offer|welcome",  # Success indicators
            r"thank you for.*apply|received.*application|application.*received",  # Applied indicators
        ]
        
        self.location_patterns = [
            r"(?:location|based in|office in):?\s*([^\n\r.!?]{3,50})",
            r"([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?)",  # City, State format
            r"(New York|San Francisco|Los Angeles|Chicago|Boston|Seattle|Austin|Denver|Remote)",
        ]
        
        # Common job sources/platforms
        self.source_mapping = {
            'linkedin.com': 'LinkedIn',
            'indeed.com': 'Indeed',
            'glassdoor.com': 'Glassdoor',
            'workatastartup.com': 'Y Combinator',
            'angel.co': 'AngelList',
            'greenhouse.io': 'Greenhouse',
            'lever.co': 'Lever',
            'ashbyhq.com': 'Ashby',
            'eightfold.ai': 'EightFold',
            'workday.com': 'Workday',
            'smartrecruiters.com': 'SmartRecruiters'
        }

    def parse_email(self, email_result) -> JobApplicationData:
        """Parse job application data from email."""
        try:
            full_text = f"{email_result.subject}\n{email_result.body}"
            
            return JobApplicationData(
                company=self._extract_company(email_result.sender, full_text),
                position=self._extract_position(email_result.subject, full_text),
                applied_date=self._format_date(email_result.date),
                status=self._extract_status(full_text),
                source=self._extract_source(email_result.sender, full_text),
                location=self._extract_location(full_text),
                job_id=self._extract_job_id(full_text),
                status_link=self._extract_links(full_text),
                email_content=full_text[:1000]  # First 1000 chars for summarization
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing email: {e}")
            return self._create_fallback_data(email_result)

    def _extract_company(self, sender: str, text: str) -> str:
        """Extract company name from sender or email content."""
        # First try to extract from sender email domain
        email_match = re.search(r"@([^.\s]+)", sender)
        if email_match:
            domain = email_match.group(1).lower()
            # Skip common email providers
            if domain not in ['gmail', 'yahoo', 'outlook', 'hotmail', 'icloud']:
                company = domain.replace('.', ' ').title()
                if len(company) > 2:
                    return company
        
        # Try patterns in text
        for pattern in self.company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    company = matches[0][1] if len(matches[0]) > 1 else matches[0][0]
                else:
                    company = matches[0]
                
                company = company.strip().title()
                if len(company) > 2 and len(company) < 50:
                    return company
        
        # Fallback to sender name
        sender_name = re.search(r"(.+?)\s*<", sender)
        if sender_name:
            name = sender_name.group(1).strip()
            if not any(word in name.lower() for word in ['noreply', 'no-reply', 'system', 'auto']):
                return name
        
        return "Unknown Company"

    def _extract_position(self, subject: str, text: str) -> str:
        """Extract job position from subject or content."""
        # Common position keywords
        positions = []
        
        # Try subject first
        subject_lower = subject.lower()
        common_titles = [
            'software engineer', 'developer', 'intern', 'internship',
            'analyst', 'manager', 'director', 'consultant', 'specialist',
            'coordinator', 'associate', 'senior', 'junior', 'lead'
        ]
        
        for title in common_titles:
            if title in subject_lower:
                # Extract surrounding context
                start = max(0, subject_lower.find(title) - 20)
                end = min(len(subject), subject_lower.find(title) + len(title) + 20)
                context = subject[start:end].strip()
                if len(context) > len(title):
                    return context
                return title.title()
        
        # Try content patterns
        for pattern in self.position_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                position = matches[0].strip()
                if 5 <= len(position) <= 100:
                    return position
        
        return "Software Engineer Intern"  # Default fallback

    def _extract_status(self, text: str) -> str:
        """Extract application status from email content."""
        text_lower = text.lower()
        
        # Check for specific status indicators
        if any(word in text_lower for word in ['unfortunately', 'regret', 'sorry to inform', 'not selected', 'declined']):
            return 'Rejected'
        
        if any(word in text_lower for word in ['congratulations', 'offer', 'pleased to inform', 'happy to inform', 'welcome']):
            return 'Offer'
        
        if any(word in text_lower for word in ['interview', 'phone screen', 'technical', 'next step', 'schedule']):
            return 'Interview'
        
        if any(word in text_lower for word in ['received', 'thank you for applying', 'application submitted']):
            return 'Applied'
        
        if any(word in text_lower for word in ['under review', 'reviewing', 'in progress']):
            return 'Under Review'
        
        return 'Applied'  # Default

    def _extract_source(self, sender: str, text: str) -> str:
        """Extract job application source/platform."""
        sender_lower = sender.lower()
        text_lower = text.lower()
        
        # Check sender domain against known sources
        for domain, source in self.source_mapping.items():
            if domain in sender_lower:
                return source
        
        # Check content for platform mentions
        for domain, source in self.source_mapping.items():
            if domain.replace('.com', '') in text_lower:
                return source
        
        # Check for direct application indicators
        if any(phrase in text_lower for phrase in ['direct', 'company website', 'career page']):
            return 'Direct Application'
        
        return 'Email'

    def _extract_location(self, text: str) -> str:
        """Extract job location from email content."""
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                location = matches[0].strip()
                if len(location) > 2 and len(location) < 100:
                    return location
        
        # Check for remote work indicators
        if any(word in text.lower() for word in ['remote', 'work from home', 'distributed', 'anywhere']):
            return 'Remote'
        
        return ''

    def _extract_job_id(self, text: str) -> str:
        """Extract job ID or reference number."""
        # Common job ID patterns
        patterns = [
            r"(?:job\s+id|job\s+#|reference|req\s+#):?\s*([a-zA-Z0-9-_]{5,50})",
            r"job/([0-9]{5,15})",
            r"jobs/view/([0-9]{5,15})",
            r"application\?code=([a-zA-Z0-9-_]{10,50})",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return ''

    def _extract_links(self, text: str) -> str:
        """Extract relevant links from email content."""
        # URL pattern
        url_pattern = r"https?://[^\s<>\"'()]+"
        urls = re.findall(url_pattern, text)
        
        # Prioritize job-related URLs
        priority_domains = [
            'greenhouse.io', 'lever.co', 'ashbyhq.com', 'workday.com',
            'linkedin.com', 'indeed.com', 'workatastartup.com'
        ]
        
        for url in urls:
            for domain in priority_domains:
                if domain in url:
                    return url
        
        # Return first URL if any
        if urls:
            return urls[0]
        
        return ''

    def _format_date(self, date: datetime) -> str:
        """Format date to YYYY-MM-DD."""
        return date.strftime("%Y-%m-%d")

    def _create_fallback_data(self, email_result) -> JobApplicationData:
        """Create fallback data structure when parsing fails."""
        return JobApplicationData(
            company="Unknown Company",
            position="Software Engineer Intern",
            applied_date=self._format_date(email_result.date),
            status="Applied",
            source="Email",
            location="",
            job_id="",
            status_link="",
            email_content=email_result.subject + " " + email_result.body[:500]
        )
