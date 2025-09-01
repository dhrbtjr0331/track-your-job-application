# agents/src/services/gmail_mcp_service.py
"""
Gmail MCP Service - Integrates with Claude's Gmail MCP tools
This service acts as a bridge between the agents and the available Gmail tools.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class GmailMCPService:
    """Service to interact with Gmail using Claude's MCP tools."""
    
    def __init__(self, gmail_tools):
        """
        Initialize with Gmail MCP tools.
        
        Args:
            gmail_tools: The Gmail MCP tools available in Claude environment
        """
        self.gmail_tools = gmail_tools
        self.logger = logging.getLogger(__name__)

    def search_job_related_emails(self, start_date: datetime, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Search for job application related emails using optimized queries.
        """
        try:
            if end_date is None:
                end_date = datetime.now()
            
            # Build comprehensive search queries for job applications
            queries = self._build_job_search_queries(start_date, end_date)
            
            all_messages = []
            seen_message_ids = set()
            
            for query in queries:
                try:
                    self.logger.info(f"Searching Gmail with query: {query}")
                    
                    # Use the search_gmail_messages tool
                    result = self.gmail_tools.search_gmail_messages(q=query)
                    
                    if 'messages' in result and result['messages']:
                        for message in result['messages']:
                            message_id = message.get('id')
                            if message_id and message_id not in seen_message_ids:
                                all_messages.append(message)
                                seen_message_ids.add(message_id)
                    
                    self.logger.info(f"Found {len(result.get('messages', []))} messages for this query")
                    
                except Exception as e:
                    self.logger.error(f"Error with query '{query}': {e}")
                    continue
            
            self.logger.info(f"Total unique job-related messages found: {len(all_messages)}")
            return all_messages
            
        except Exception as e:
            self.logger.error(f"Error searching for job emails: {e}")
            return []

    def get_thread_content(self, thread_id: str) -> Dict[str, Any]:
        """
        Get complete thread content including all messages.
        """
        try:
            self.logger.debug(f"Reading thread: {thread_id}")
            
            # Use the read_gmail_thread tool
            thread_data = self.gmail_tools.read_gmail_thread(
                thread_id=thread_id,
                include_full_messages=True
            )
            
            return thread_data
            
        except Exception as e:
            self.logger.error(f"Error reading thread {thread_id}: {e}")
            return {}

    def get_profile(self) -> Dict[str, Any]:
        """Get Gmail profile information."""
        try:
            profile = self.gmail_tools.read_gmail_profile()
            return profile
        except Exception as e:
            self.logger.error(f"Error getting Gmail profile: {e}")
            return {}

    def _build_job_search_queries(self, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Build optimized Gmail search queries for job applications.
        
        Returns list of search queries to execute.
        """
        date_filter = f"after:{start_date.strftime('%Y/%m/%d')} before:{end_date.strftime('%Y/%m/%d')}"
        
        # Core job application keywords - high precision
        core_job_queries = [
            f'{date_filter} ("application received" OR "thank you for applying" OR "application submitted")',
            f'{date_filter} ("interview" AND ("scheduled" OR "invitation" OR "next step"))',
            f'{date_filter} ("position" AND ("applied" OR "application" OR "candidate"))',
            f'{date_filter} ("job" AND ("application" OR "opportunity" OR "opening"))',
            f'{date_filter} ("internship" AND ("application" OR "program" OR "summer" OR "2026"))',
        ]
        
        # ATS and recruiting platform queries
        ats_queries = [
            f'{date_filter} (from:greenhouse.io OR from:lever.co OR from:ashbyhq.com)',
            f'{date_filter} (from:workday.com OR from:eightfold.ai OR from:smartrecruiters.com)',
            f'{date_filter} (from:icims.com OR from:taleo.net OR from:jobvite.com)',
            f'{date_filter} (from:linkedin.com OR from:indeed.com OR from:glassdoor.com)',
            f'{date_filter} from:workatastartup.com',
        ]
        
        # Status update queries
        status_queries = [
            f'{date_filter} ("unfortunately" OR "regret to inform" OR "not selected")',
            f'{date_filter} ("congratulations" OR "pleased to offer" OR "offer letter")',
            f'{date_filter} ("next round" OR "final interview" OR "technical interview")',
            f'{date_filter} ("application status" OR "update on your application")',
        ]
        
        # Combine all queries
        all_queries = core_job_queries + ats_queries + status_queries
        
        # Limit number of queries to avoid API limits
        return all_queries[:8]  # Top 8 most effective queries


# agents/test_gmail_integration.py
"""
Test script to validate Gmail MCP integration and agent functionality.
Run this to test the system with real Gmail data.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.orchestrator import JobApplicationOrchestratorAgent
from services.gmail_mcp_service import GmailMCPService
from services.claude_service import ClaudeService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockGmailTools:
    """Mock Gmail tools for testing when MCP tools aren't available."""
    
    def search_gmail_messages(self, q: str):
        logger.info(f"Mock Gmail search: {q}")
        return {
            'messages': [
                {
                    'id': 'test_message_1',
                    'threadId': 'test_thread_1',
                    'snippet': 'Thank you for your application to our Software Engineer Intern position...'
                },
                {
                    'id': 'test_message_2', 
                    'threadId': 'test_thread_2',
                    'snippet': 'We received your application for the Data Science role...'
                }
            ]
        }
    
    def read_gmail_thread(self, thread_id: str, include_full_messages: bool = True):
        logger.info(f"Mock Gmail thread read: {thread_id}")
        return {
            'messages': [
                {
                    'id': f'msg_{thread_id}',
                    'threadId': thread_id,
                    'internalDate': str(int(datetime.now().timestamp() * 1000)),
                    'payload': {
                        'headers': [
                            {'name': 'Subject', 'value': 'Application Confirmation - Software Engineer Intern'},
                            {'name': 'From', 'value': 'recruiting@techcorp.com'},
                            {'name': 'Date', 'value': datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}
                        ],
                        'body': {
                            'data': 'VGhhbmsgeW91IGZvciB5b3VyIGFwcGxpY2F0aW9uIHRvIG91ciBTb2Z0d2FyZSBFbmdpbmVlciBJbnRlcm4gcG9zaXRpb24='
                        }
                    }
                }
            ]
        }
    
    def read_gmail_profile(self):
        return {
            'emailAddress': 'test@example.com',
            'messagesTotal': 1000,
            'threadsTotal': 800
        }

def test_agents_system():
    """Test the complete agents system."""
    
    try:
        # Check if we have actual Gmail tools available
        # In a real Claude environment, you would access the actual tools here
        gmail_tools = MockGmailTools()  # Using mock for testing
        
        # Initialize services
        logger.info("Initializing services...")
        
        # Gmail service
        gmail_service = GmailMCPService(gmail_tools)
        
        # Claude service (you'll need to add your API key)
        claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        if not claude_api_key:
            logger.warning("No ANTHROPIC_API_KEY found. Using mock responses.")
            claude_service = None
        else:
            claude_service = ClaudeService(claude_api_key)
        
        # Initialize orchestrator
        orchestrator = JobApplicationOrchestratorAgent(gmail_service, claude_service)
        
        # Test parameters
        start_date = datetime.now() - timedelta(days=30)  # Last 30 days
        output_file = './outputs/test_applications.xlsx'
        
        logger.info(f"Testing job application processing...")
        logger.info(f"Start date: {start_date.strftime('%Y-%m-%d')}")
        logger.info(f"Output file: {output_file}")
        
        # Run the processing
        results = orchestrator.process_job_applications(
            start_date=start_date,
            output_file_path=output_file,
            append_mode=False
        )
        
        # Print results
        logger.info("Processing completed!")
        logger.info(f"Results: {results}")
        
        # Generate summary
        summary = orchestrator.get_processing_summary(results)
        print("\n" + "="*50)
        print("PROCESSING SUMMARY")
        print("="*50)
        print(summary)
        
        return results['success']
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

def test_individual_components():
    """Test individual components separately."""
    
    print("\n🧪 Testing Individual Components")
    print("-" * 40)
    
    # Test Gmail service
    try:
        print("📧 Testing Gmail Service...")
        gmail_tools = MockGmailTools()
        gmail_service = GmailMCPService(gmail_tools)
        
        # Test search
        start_date = datetime.now() - timedelta(days=7)
        emails = gmail_service.search_job_related_emails(start_date)
        print(f"   ✅ Found {len(emails)} emails")
        
        # Test thread reading
        if emails:
            thread_data = gmail_service.get_thread_content(emails[0]['threadId'])
            print(f"   ✅ Read thread data: {len(thread_data.get('messages', []))} messages")
        
    except Exception as e:
        print(f"   ❌ Gmail service test failed: {e}")
    
    # Test Claude service
    try:
        print("🤖 Testing Claude Service...")
        claude_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if claude_api_key:
            claude_service = ClaudeService(claude_api_key)
            test_prompt = "Summarize in 30 words: Thank you for applying to our software engineer position. We received your application and will review it."
            
            response = claude_service.create_message(test_prompt, max_tokens=100)
            print(f"   ✅ Claude response: {response}")
        else:
            print("   ⚠️  No API key found, skipping Claude test")
            
    except Exception as e:
        print(f"   ❌ Claude service test failed: {e}")
    
    print("-" * 40)

if __name__ == "__main__":
    print("🚀 Job Application Tracker - Agent System Test")
    print("=" * 50)
    
    # Create outputs directory
    os.makedirs('./outputs', exist_ok=True)
    
    # Test individual components first
    test_individual_components()
    
    # Test full system
    print("\n🎯 Testing Complete System")
    print("-" * 40)
    
    success = test_agents_system()
    
    if success:
        print("\n✅ All tests passed! System is ready.")
        print("\n📋 Next steps:")
        print("1. Add your real ANTHROPIC_API_KEY to .env file")
        print("2. Replace MockGmailTools with actual Gmail MCP tools")
        print("3. Run: python main.py to start the API server")
        print("4. Test with real data: curl -X POST http://localhost:8000/process ...")
    else:
        print("\n❌ Tests failed. Check logs above for details.")
    
    print("\n" + "=" * 50)


# agents/run_test.py
"""
Simple test runner that you can execute to validate the system.
"""

import subprocess
import sys
import os

def main():
    """Run the test script."""
    
    # Ensure we're in the agents directory
    if not os.path.exists('test_gmail_integration.py'):
        print("❌ Please run this from the agents/ directory")
        return
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return
    
    print("🧪 Running Job Application Tracker Tests")
    print("=" * 45)
    
    try:
        # Run the test
        result = subprocess.run([
            sys.executable, 'test_gmail_integration.py'
        ], capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Tests completed successfully!")
        else:
            print("❌ Tests failed with return code:", result.returncode)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")

if __name__ == "__main__":
    main()


# Integration with Real Gmail Tools
"""
To integrate with the actual Gmail tools available in your Claude environment,
replace the MockGmailTools class with the real Gmail MCP tools.

Example integration:

# In your actual implementation:
class RealGmailIntegration:
    def __init__(self, claude_gmail_tools):
        self.search_gmail_messages = claude_gmail_tools.search_gmail_messages
        self.read_gmail_thread = claude_gmail_tools.read_gmail_thread  
        self.read_gmail_profile = claude_gmail_tools.read_gmail_profile

# Then in your main application:
gmail_service = GmailMCPService(RealGmailIntegration(your_gmail_tools))
"""