#!/usr/bin/env python3
"""
Gmail Job Application Processor - Claude Interface Version
Run this code directly in Claude's interface where Gmail MCP tools are available.
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List

def process_job_applications_in_claude():
    """
    Process job applications using Gmail MCP tools available in Claude.
    Copy and run this code in Claude's interface.
    """
    
    print("🔍 Searching for job applications...")
    
    # Search query for job applications
    query = 'after:2025/08/01 ("thank you for your interest" OR "application received" OR "internship" OR "summer 2026")'
    
    # This will work in Claude interface:
    # result = search_gmail_messages(q=query)
    
    print(f"Search query: {query}")
    print("📋 To run this:")
    print("1. Copy this code into Claude's interface")
    print("2. Replace the print statement with actual Gmail search")
    print("3. Process the results")
    
    return """
    # Copy this code and run it in Claude:
    
    # Search for job applications
    result = search_gmail_messages(q='after:2025/08/01 ("thank you for your interest" OR "application received")')
    
    # Process the results here
    print("Found job applications:", result)
    """

if __name__ == "__main__":
    code_to_run = process_job_applications_in_claude()
    print(code_to_run)
