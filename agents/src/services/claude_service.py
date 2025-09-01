# agents/src/services/claude_service.py
import anthropic
import logging
from typing import Optional

class ClaudeService:
    """Service to interact with Claude API."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    def create_message(self, 
                      prompt: str, 
                      model: str = "claude-3-sonnet-20240229",
                      max_tokens: int = 1000,
                      temperature: float = 0.3) -> Optional[str]:
        """Create a message using Claude API."""
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Error calling Claude API: {e}")
            return None
