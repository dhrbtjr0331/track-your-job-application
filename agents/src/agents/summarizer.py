# agents/src/agents/summarizer.py
import re
from typing import List
import logging

class SummarizerAgent:
    """Agent responsible for creating concise summaries of job application emails using Claude."""
    
    def __init__(self, claude_client):
        self.claude_client = claude_client
        self.logger = logging.getLogger(__name__)
        self.max_words = 30

    def summarize_email(self, job_data) -> str:
        """Create a concise summary of the job application email."""
        try:
            # Prepare content for summarization
            content = self._prepare_content(job_data)
            
            # Create prompt for Claude
            prompt = self._create_summary_prompt(content, job_data)
            
            # Get summary from Claude
            summary = self._get_claude_summary(prompt)
            
            # Clean and validate summary
            return self._clean_summary(summary)
            
        except Exception as e:
            self.logger.error(f"Error creating summary: {e}")
            return self._create_fallback_summary(job_data)

    def _prepare_content(self, job_data) -> str:
        """Prepare email content for summarization."""
        # Clean and truncate content
        content = job_data.email_content
        
        # Remove excessive whitespace and clean up
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[^\w\s.,!?@()-]', '', content)
        
        # Limit content length for API efficiency
        return content[:2000]

    def _create_summary_prompt(self, content: str, job_data) -> str:
        """Create prompt for Claude API."""
        return f"""
Please create a very concise summary (maximum 30 words) of this job application email.

Company: {job_data.company}
Position: {job_data.position}
Status: {job_data.status}

Email content:
{content}

Focus on:
- Key application details
- Current status
- Any important next steps
- Platform/source used

Summary (max 30 words):
"""

    def _get_claude_summary(self, prompt: str) -> str:
        """Get summary from Claude API."""
        try:
            # This would use your actual Claude client
            # For now, returning a placeholder
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise

    def _clean_summary(self, summary: str) -> str:
        """Clean and validate the summary."""
        # Remove any quotation marks
        summary = summary.strip('"\'')
        
        # Ensure it's not too long
        words = summary.split()
        if len(words) > self.max_words:
            summary = ' '.join(words[:self.max_words])
        
        # Ensure it ends properly
        if not summary.endswith(('.', '!', '?')):
            summary += '.'
        
        return summary

    def _create_fallback_summary(self, job_data) -> str:
        """Create a fallback summary when API fails."""
        source = job_data.source if job_data.source else "email"
        status = job_data.status.lower()
        
        if status == 'applied':
            return f"Applied to {job_data.company} via {source}. Application confirmation received."
        elif status == 'rejected':
            return f"{job_data.company} application status: Not selected for {job_data.position}."
        elif status == 'interview':
            return f"{job_data.company} interview scheduled for {job_data.position}."
        elif status == 'offer':
            return f"Job offer received from {job_data.company} for {job_data.position}."
        else:
            return f"{job_data.company} application via {source} - {status}."
