# agents/src/services/gmail_service.py
import logging
from typing import List, Dict, Any, Optional

class GmailService:
    """Service to interact with Gmail MCP tools."""
    
    def __init__(self, gmail_tools):
        self.gmail_tools = gmail_tools
        self.logger = logging.getLogger(__name__)

    def search_messages(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search Gmail messages using the search tool."""
        try:
            # Use the search_gmail_messages tool
            result = self.gmail_tools.search_gmail_messages(q=query)
            
            messages = []
            if 'messages' in result:
                messages = result['messages'][:max_results]
            
            self.logger.info(f"Found {len(messages)} messages for query: {query}")
            return messages
            
        except Exception as e:
            self.logger.error(f"Error searching Gmail: {e}")
            return []

    def read_thread(self, thread_id: str) -> Dict[str, Any]:
        """Read a complete Gmail thread."""
        try:
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
