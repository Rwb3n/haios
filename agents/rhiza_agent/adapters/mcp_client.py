"""
MCP Client for communicating with Claude-as-a-Service.

This client provides a simple interface for Python adapters to query
the Claude MCP server, which automatically includes project context
from CLAUDE.md and provides centralized governance.
"""

import httpx
import json
from typing import Dict, Optional, Any
from datetime import datetime, UTC
import os
import time


class MCPClient:
    """Client for communicating with Claude MCP server."""
    
    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            server_url: URL of the Claude MCP server. 
                       Defaults to http://claude-server:8090 or env var MCP_SERVER_URL
        """
        self.server_url = server_url or os.getenv(
            "MCP_SERVER_URL", 
            "http://claude-server:8090"
        )
        self.client = httpx.Client(timeout=60.0)
        self._check_health()
    
    def _check_health(self, retries: int = 3, delay: float = 2.0) -> bool:
        """Check server health with retries."""
        for i in range(retries):
            if self.health_check():
                return True
            if i < retries - 1:
                time.sleep(delay)
        return False
    
    def query(self, 
              prompt: str, 
              context: Optional[Dict[str, Any]] = None,
              max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Send a query to the Claude MCP server.
        
        Args:
            prompt: The prompt to send to Claude
            context: Optional additional context
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing the response or error information
        """
        request_data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": f"mcp-{int(time.time() * 1000)}"
        }
        
        if context:
            request_data["context"] = context
        
        try:
            response = self.client.post(
                f"{self.server_url}/query",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException:
            return {
                "error": "Request timed out",
                "type": "timeout_error",
                "trace_id": request_data["trace_id"]
            }
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "type": "http_error",
                "trace_id": request_data["trace_id"]
            }
        except Exception as e:
            return {
                "error": str(e),
                "type": "mcp_client_error",
                "trace_id": request_data["trace_id"]
            }
    
    def query_structured(self,
                        prompt: str,
                        response_format: Dict[str, Any],
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query with structured output format.
        
        Args:
            prompt: The prompt to send
            response_format: Expected response structure
            context: Optional additional context
            
        Returns:
            Structured response matching the format
        """
        enhanced_prompt = f"""{prompt}

Please respond with valid JSON matching this structure:
{json.dumps(response_format, indent=2)}
"""
        
        response = self.query(enhanced_prompt, context)
        
        if "error" in response:
            return response
        
        # Try to parse structured response
        try:
            if "content" in response:
                return json.loads(response["content"])
            return response
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse structured response",
                "type": "parse_error",
                "raw_response": response
            }
    
    def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            response = self.client.get(
                f"{self.server_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class MockMCPClient(MCPClient):
    """Mock MCP client for testing without a real server."""
    
    def __init__(self, mock_responses: Optional[Dict[str, Any]] = None):
        """Initialize mock client with predefined responses."""
        self.server_url = "mock://localhost"
        self.mock_responses = mock_responses or {}
        self.query_history = []
    
    def _check_health(self, retries: int = 3, delay: float = 2.0) -> bool:
        """Mock health check always returns True."""
        return True
    
    def query(self, 
              prompt: str, 
              context: Optional[Dict[str, Any]] = None,
              max_tokens: int = 2000) -> Dict[str, Any]:
        """Return mock response based on prompt keywords."""
        # Record the query
        self.query_history.append({
            "prompt": prompt,
            "context": context,
            "timestamp": datetime.now(UTC).isoformat()
        })
        
        # Check for predefined responses
        for keyword, response in self.mock_responses.items():
            if keyword.lower() in prompt.lower():
                return response
        
        # Default mock response
        return {
            "content": json.dumps({
                "themes": [
                    {
                        "name": "Distributed Trust Systems",
                        "relevance_score": 9,
                        "description": "Mock theme for testing"
                    }
                ],
                "analysis": "Mock analysis response",
                "recommendations": ["Mock recommendation"]
            }),
            "model": "mock-claude",
            "timestamp": datetime.now(UTC).isoformat()
        }
    
    def health_check(self) -> bool:
        """Mock health check."""
        return True