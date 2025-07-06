# Rhiza Agent Blueprint v3: Claude-as-a-Service Architecture

**Date**: 2025-07-04  
**Status**: In Development  
**Supersedes**: rhiza_blueprint_v2.md

## Executive Summary

This blueprint represents a fundamental architectural pivot for the Rhiza system, moving from direct API calls to a Claude-as-a-Service model using `claude mcp serve`. This change provides centralized governance, automatic context management, and simplified adapter code.

## Architectural Overview

### Previous Architecture (v2)
```
Python Adapter → httpx → Anthropic API
```

### New Architecture (v3)
```
Python Adapter → MCP Client → claude-server → Anthropic API
                               ↓
                         CLAUDE.md context
```

## Key Benefits

1. **Unified Context Management**: Claude server automatically loads project context
2. **Centralized Governance**: Single audit/control point for all LLM calls
3. **Simplified Adapters**: No auth, retry logic, or context injection needed
4. **Future-Proof**: Easy to swap LLM providers without changing adapters
5. **Hook Integration**: Apply HAiOS hooks to the central server

## Implementation Plan

### Stage 1: Infrastructure Setup

#### 1.1 Claude Server Docker Image

Create `claude-server/Dockerfile`:
```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI
RUN curl -fsSL https://console.anthropic.com/install.sh | sh

# Set up working directory
WORKDIR /app

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
```

#### 1.2 Docker Compose Integration

Update `docker-compose.yml`:
```yaml
services:
  claude-server:
    build:
      context: .
      dockerfile: claude-server/Dockerfile
    command: ["claude", "mcp", "serve", "--port", "8090"]
    volumes:
      - .:/app/project:ro  # Read-only mount of project
    working_dir: /app/project
    networks:
      - localnet
    env_file: .env
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8090/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Stage 2: MCP Client Library

#### 2.1 Create MCP Client Base Class

`adapters/mcp_client.py`:
```python
import httpx
import json
from typing import Dict, Optional
from datetime import datetime, UTC

class MCPClient:
    """Client for communicating with Claude MCP server."""
    
    def __init__(self, server_url: str = "http://claude-server:8090"):
        self.server_url = server_url
        self.client = httpx.Client(timeout=60.0)
    
    def query(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Send a query to the Claude MCP server."""
        request_data = {
            "prompt": prompt,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        if context:
            request_data["context"] = context
        
        try:
            response = self.client.post(
                f"{self.server_url}/query",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "error": str(e),
                "type": "mcp_client_error"
            }
    
    def health_check(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            response = self.client.get(f"{self.server_url}/health")
            return response.status_code == 200
        except:
            return False
```

### Stage 3: Adapter Refactoring

#### 3.1 Updated Phase 1 Adapter

`adapters/phase1_strategic_triage_v3.py`:
```python
from typing import List, Dict, Any
from datetime import datetime, UTC
import json
from .base_agent import BaseRhizaAgent
from .mcp_client import MCPClient

class StrategicTriageAgent(BaseRhizaAgent):
    def __init__(self):
        super().__init__()
        self.mcp_client = MCPClient()
    
    def analyze_research_landscape(self, 
                                 corpus_source: str,
                                 categories: List[str]) -> Dict[str, Any]:
        """Analyze research corpus using Claude-as-a-Service."""
        
        # Generate evidence
        evidence = self.generate_evidence({
            'action': 'analyze_research_landscape',
            'corpus_source': corpus_source,
            'categories': categories,
            'timestamp': datetime.now(UTC).isoformat()
        })
        
        # Fetch recent papers
        recent_papers = self._fetch_recent_papers(corpus_source, categories)
        
        if not recent_papers:
            return self._empty_result(evidence, corpus_source, categories)
        
        # Simple prompt - context is handled by the server
        prompt = f"""
Analyze these research papers and identify the top 3-5 themes most relevant to HAiOS.

Papers:
{json.dumps(recent_papers, indent=2)}

Return a structured analysis with:
1. Identified themes with relevance scores (1-10)
2. Key papers for each theme
3. Open questions that could be addressed
"""
        
        # Query Claude server (which has full HAiOS context)
        response = self.mcp_client.query(prompt)
        
        if "error" in response:
            self.log_error(f"MCP query failed: {response['error']}")
            return self._fallback_analysis(recent_papers, evidence)
        
        # Structure the response
        return self._structure_priorities(response, evidence)
```

### Stage 4: Migration Strategy

#### 4.1 Parallel Testing
1. Keep existing adapters (v2) operational
2. Create v3 adapters alongside
3. Test both versions in parallel
4. Gradually switch n8n workflows to v3

#### 4.2 Rollback Plan
- Docker compose profiles to switch between v2/v3
- Feature flags in n8n workflows
- Keep v2 adapters for 30 days after v3 go-live

### Stage 5: Advanced Features

#### 5.1 Hook Integration
```python
# In claude-server/hooks.py
class LLMGovernanceHook:
    def pre_query(self, request):
        """Log and validate before LLM call."""
        # Log the query
        logger.info(f"LLM Query: {request['prompt'][:100]}...")
        
        # Check for sensitive data
        if self._contains_sensitive_data(request['prompt']):
            raise SecurityError("Sensitive data detected")
        
        return request
    
    def post_query(self, response):
        """Process response after LLM call."""
        # Add metadata
        response['metadata'] = {
            'timestamp': datetime.now(UTC).isoformat(),
            'model': 'claude-3-haiku'
        }
        return response
```

#### 5.2 Caching Layer
- Redis cache for repeated queries
- TTL based on query type
- Cache invalidation on context updates

## Testing Strategy

### Unit Tests
- Mock MCP server responses
- Test error handling
- Validate request/response format

### Integration Tests
- Test with real Claude server
- Verify context loading
- Test hook execution

### Performance Tests
- Response time comparison (v2 vs v3)
- Concurrent request handling
- Cache hit rates

## Security Considerations

1. **Network Isolation**: Claude server only accessible within Docker network
2. **Read-Only Mounts**: Project files mounted read-only
3. **API Key Management**: Centralized in claude-server
4. **Audit Logging**: All queries logged with trace IDs
5. **Rate Limiting**: Implement at server level

## Monitoring & Observability

1. **Metrics**:
   - Query count and latency
   - Error rates by type
   - Cache hit/miss rates
   - Token usage

2. **Logging**:
   - Structured JSON logs
   - Trace ID propagation
   - Query/response pairs (redacted)

3. **Alerts**:
   - High error rates
   - Slow response times
   - API quota warnings

## Development Checklist

- [ ] Create claude-server Docker image
- [ ] Implement MCP client library
- [ ] Refactor Phase 1 adapter
- [ ] Refactor Phase 2 adapter
- [ ] Refactor Phase 3 adapter
- [ ] Create integration tests
- [ ] Update n8n workflows
- [ ] Document deployment process
- [ ] Set up monitoring
- [ ] Conduct security review

## Conclusion

The Claude-as-a-Service architecture represents a significant improvement in governance, maintainability, and extensibility. By centralizing LLM interactions through a managed service, we gain better control while simplifying our adapter code.

This architecture aligns perfectly with HAiOS principles:
- **Evidence-Based**: All LLM calls are logged and auditable
- **Separation of Duties**: Adapters focus on business logic, not infrastructure
- **Structured Mistrust**: Central governance point for all AI interactions

The implementation will proceed iteratively, maintaining backward compatibility until the new system is proven stable.