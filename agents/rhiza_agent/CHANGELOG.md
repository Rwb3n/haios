# Rhiza Agent Development Changelog

## [v3.0] - 2025-07-04 - Claude-as-a-Service Architecture

### Added
- **Claude-as-a-Service Architecture (v3)**
  - Created `rhiza_blueprint_v3.md` with complete architectural design
  - Implemented `claude-server/` Docker infrastructure
    - Custom Dockerfile for Claude CLI integration
    - Health check and startup scripts
  - Built `adapters/mcp_client.py` - MCP client library with mock support
  - Created `adapters/phase1_strategic_triage_v3.py` - First v3 adapter
  - Added claude-server service to docker-compose.yml
  - Created `test_mvp_v3.sh` for v3 testing

### Changed
- **Directory Organization**
  - All JSON outputs now save to `reports/` subdirectory
  - Moved stray artifacts to proper locations
  
### Fixed
- **Technical Debt**
  - Replaced deprecated `datetime.utcnow()` with `datetime.now(UTC)` in all adapters
  - Added error handling for empty arXiv API responses
  - Added XML parsing error handling with proper logging

### Architecture Shift
- **From**: Direct API calls (`Python → Anthropic API`)
- **To**: Centralized service (`Python → MCP Client → Claude Server → Anthropic API`)
- **Benefits**: Automatic context loading, centralized governance, simplified adapters

---

## [v2.0] - 2025-07-04 - MVP Validation Complete

### Completed
- **Three-Phase Pipeline Operational**
  - Phase 1: Strategic Triage - Identifies high-priority themes
  - Phase 2: Tactical Ingestion - Categorizes papers by tier
  - Phase 3: Crystal Seed Extraction - Extracts actionable insights
  
- **Testing Infrastructure**
  - Created `test_mvp.sh` for end-to-end testing
  - Mock LLM support for testing without API keys
  - Deterministic keyword matching in Phase 2

- **n8n Integration**
  - Created `n8n_workflows/rhiza_mvp_linear.json`
  - Sequential workflow with conditional execution
  - Ready for deployment

### Validated
- All acceptance criteria from blueprint v2 met
- System works end-to-end with mock data
- Clear separation of concerns between phases
- No premature optimization or security implementation

### Documentation
- Created `validation_report_mvp.md` with full test results
- Identified next steps for iterative improvement

---

## [v1.0] - 2025-07-03 - Initial Blueprint

### Created
- **Foundation Documents**
  - `rhiza_blueprintv2.md` - Iterative development approach
  - Initial adapter structure
  - Three-phase architecture design

### Design Decisions
- Start with MVP, not production-ready system
- Mock LLM first, real integration later
- Linear workflow before complex orchestration
- Focus on functionality over security initially

---

## Development Timeline

1. **2025-07-03**: Initial blueprint and design
2. **2025-07-04 Morning**: MVP implementation and testing
3. **2025-07-04 Afternoon**: v3 architecture pivot based on Claude MCP feedback

## Current Status

- **MVP**: ✅ Complete and validated
- **v3 Architecture**: 🚧 In progress (Phase 1 complete)
- **Production Ready**: ❌ Not yet (needs v3 completion, security, monitoring)

## Next Milestones

1. Complete v3 adapter refactoring (Phase 2 & 3)
2. Deploy and test with real Claude server
3. Implement governance hooks and monitoring
4. Add security layers per blueprint stages
5. Performance optimization and caching