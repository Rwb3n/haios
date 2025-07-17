# Claude Code SDK Reference - v2 Pattern (HAiOS COMPLIANT)

## Core Paradigm - v2 STANDARD (HAiOS THREE PILLARS)

**NO CONTENT EMBEDDING IN PROMPTS - EVER**

This pattern implements HAiOS's Three Pillars:
1. **Evidence-Based Development**: All operations produce verifiable file artifacts
2. **Durable, Co-located Context**: Context lives in files, not embedded in prompts
3. **Separation of Duties**: Orchestrator controls metadata, agents control content only

Agents receive ONLY simple file operation instructions:
- "Read this file"
- "Edit this file" 
- "Write this file"

Content lives in files, not in prompt instructions. If an agent needs context (ADR content, dialogue data, etc.), they read it from a file using the Read tool.

**VIOLATION EXAMPLES (NEVER DO THIS):**
```
❌ "Here is the dialogue data: {json.dumps(data)}"
❌ "Update the summary with this content: [embedded content]"
❌ "Consider this ADR: [embedded ADR text]"
```

**CORRECT v2 PATTERN:**
```
✅ "Read dialogue.json then read summary.md then use Edit to update summary"
✅ "Read ADR-OS-001.md then use Edit to append your response"
✅ "Read prompt.txt then read dialogue.json then use Edit to add entry"
```

## Available Tools

| Tool | Description | Permission Required |
|------|-------------|-------------------|
| Bash | Executes shell commands in your environment | Yes |
| Edit | Makes targeted edits to specific files | Yes |
| Glob | Finds files based on pattern matching | No |
| Grep | Searches for patterns in file contents | No |
| LS | Lists files and directories | No |
| MultiEdit | Performs multiple edits on a single file atomically | Yes |
| NotebookEdit | Modifies Jupyter notebook cells | Yes |
| NotebookRead | Reads and displays Jupyter notebook contents | No |
| Read | Reads the contents of files | No |
| Task | Runs a sub-agent to handle complex, multi-step tasks | No |
| TodoWrite | Creates and manages structured task lists | No |
| WebFetch | Fetches content from a specified URL | Yes |
| WebSearch | Performs web searches with domain filtering | Yes |
| Write | Creates or overwrites files | Yes |

## 2A Agent Tool Assignments

### Standard Pattern (All Agents)
- **Base Access**: `["Read"]` (no permission required)
- **File Operations**: `["Read", "Edit"]` for file modifications
- **File Creation**: `["Read", "Write"]` for new file creation

### Agent-Specific Tools - v2.0 ENHANCED

#### ReadPromptNode (Step 1) - ATOMIC PATTERN
- **Implementation**: Atomic prompt file reading with validation
- **Tools**: `["Read"]` (read-only access)
- **Purpose**: Read prompt files with comprehensive validation
- **Pattern**: Single atomic operation with file access validation
- **Tool Count**: 1 tool (Read prompt file)
- **Validation**: File access validation, read-only access confirmation

#### UpdateDialogueNode (Step 2) - ATOMIC PATTERN  
- **Implementation**: Atomic dialogue updates with skeleton creation
- **Tools**: `["Read", "Edit"]`
- **Purpose**: Create dialogue skeletons, get agent responses, update dialogue
- **Pattern**: Skeleton creation → Agent response → Dialogue update
- **Tool Count**: 2 tools (Read dialogue, Edit dialogue)
- **Validation**: Skeleton creation, tool usage, operation completion

#### SummarizerNode (Step 3) - SCRIBE PATTERN
- **Implementation**: Dialogue summarization with file access validation
- **Tools**: `["Read", "Edit"]` 
- **Purpose**: Read dialogue data, update summary files
- **Pattern**: Read dialogue.json, read summary.md, edit summary.md
- **Instruction Example**: `"Read dialogue.json then read summary.md then use Edit to update summary"`
- **Tool Count**: MUST use 3 tools (Read dialogue, Read summary, Edit summary)
- **Validation**: File access validation, tool usage validation, completion validation

#### ConsensusSynthesisNode (Step 4) - SYNTHESIS PATTERN
- **Implementation**: Professional deliverable generation with skeleton creation
- **Tools**: `["Read", "Edit"]`
- **Purpose**: Create consensus synthesis with implementation roadmap
- **Pattern**: Skeleton creation → Multi-file reading → Content synthesis
- **Tool Count**: 3+ tools (Read dialogue, Read synthesis, Edit synthesis with multiple edits)
- **Validation**: Skeleton creation, file access validation, tool usage validation, completion validation

#### Legacy Nodes (Deprecated)
- **Architect1Node/Architect2Node**: Replaced by ReadPromptNode + UpdateDialogueNode atomic chains
- **DialogueSummaryNode**: Replaced by ConsensusSynthesisNode professional deliverable
- **Location**: `nodes/__legacy/` directory

## Orchestrator Responsibilities - v2 HARDENED PATTERN (HAiOS STANDARD)

### HAiOS Separation of Duties Implementation

- **Skeleton Entry Creation**: Orchestrator ALWAYS pre-creates skeleton entries with role, round, timestamp
- **Agent Content Only**: Agents ONLY fill in the content field of pre-created entries  
- **Metadata Control**: Role names come from prompt file headers, NOT agent hallucination
- **File Operations**: Orchestrator tells agents which files to read/edit
- **Simple Instructions**: "Read file then use Edit to fill content field of last entry"

### HAiOS-Compliant Entry Pattern (v1.3)
```json
// Step 1: Orchestrator creates skeleton BEFORE calling agent
{
  "round": 1,
  "role": "Architect-1",              // Extracted from <Architect-1 Prompt: ...>
  "timestamp": "2025-07-16T18:27:27.123",  // Orchestrator controlled
  "content": "",                      // Agent fills with response
  "consensus": false                  // Agent can set to true if consensus reached
}

// Step 2: Agent receives instruction
"Read dialogue.json then use Edit to fill in the content field of the last entry.
IMPORTANT: If consensus reached, also set consensus field to true."

// Step 3: Agent can modify content and consensus fields only
```

### Consensus Detection Enhancement (v1.3.1) - Dual-Mode Approach

**Primary Method: Boolean Field (Structured)**
- **Either architect** can set `"consensus": true` in dialogue entry when consensus reached
- Detection: `entry.consensus === true` checked after every agent response
- Benefits: Explicit, unambiguous, intentional consensus declaration
- Logging: `[CONSENSUS] Detected consensus signal (boolean field) from {architect_name}`

**Fallback Method: Pattern Matching (Natural Language)**
- Scans content for consensus language patterns from **either architect**
- Patterns: `"UNANIMOUS APPROVAL"`, `"DIALOGUE COMPLETE"`, `"**No Further Dissent**"`, `"Complete Agreement"`, `"APPROVED FOR IMPLEMENTATION"`, `"production-ready"`, etc.
- Benefits: Backwards compatibility with existing dialogues
- Logging: `[CONSENSUS] Detected consensus signal (pattern fallback) from {architect_name}`

**Critical Fix (v1.3.1):**
- **Before**: Consensus only detected after Architect-2 responses
- **After**: Consensus detected immediately from either Architect-1 or Architect-2
- **Result**: No more missed consensus signals, immediate dialogue termination

**Why Dual-Mode:**
✅ **Forward Compatibility**: New sessions use structured boolean approach
✅ **Backwards Compatibility**: Existing sessions continue to work with pattern matching  
✅ **Progressive Enhancement**: System becomes more reliable over time
✅ **No Breaking Changes**: Zero disruption to existing dialogues
✅ **Immediate Detection**: Either architect can end dialogue without waiting for next response

### Consensus Synthesis Enhancement (v1.4) - SDK REFERENCE COMPLIANT

**ConsensusSynthesisNode** - Follows Proven Scribe Pattern

- **Trigger**: Automatically invoked when consensus is achieved via any method
- **Pattern**: SDK Reference Scribe pattern (lines 67-72) - proven 3-tool approach
- **Tools**: `["Read", "Edit"]` - Standard file modification pattern (line 56)
- **Tool Count**: Exactly 3 tools - Read dialogue + Read synthesis skeleton + Edit synthesis
- **Process**:
  1. **Prep**: Read dialogue.json to extract metadata (question, ADR context)
  2. **Exec**: Create structured consensus_synthesis.md skeleton with rich placeholders
  3. **Post**: Agent instruction: "Read dialogue.json then read consensus_synthesis.md then use Edit to fill placeholders"
- **Instruction Pattern**: Direct instruction like other nodes (no intermediate prompt files)
- **Output**: Professional `consensus_synthesis.md` with implementation roadmap and stakeholder content
- **Fallback**: Creates basic skeleton if dialogue reading fails

**SDK Reference Compliance:**
✅ **Tool Assignment**: Uses `["Read", "Edit"]` for file modifications (line 56)  
✅ **Scribe Pattern**: 3 tools exactly - matches proven pattern (line 72)  
✅ **HAiOS Skeleton**: Orchestrator creates structure, agent fills content (lines 74-76)  
✅ **No Content Embedding**: Agent reads context from files, not embedded prompts  
✅ **Direct Instructions**: No intermediate prompt files like other nodes  
✅ **Separation of Duties**: Clear boundary between orchestrator and agent responsibilities

**vs SummarizerNode:**
- **SummarizerNode**: Tracks ongoing dialogue evolution (runs every round)
- **ConsensusSynthesisNode**: Creates final architectural deliverable (runs once at consensus)
- **SummarizerNode Output**: `summary.md` with current state and open questions
- **ConsensusSynthesisNode Output**: `consensus_synthesis.md` with implementation roadmap and decisions

**Benefits:**
✅ **Final Deliverable**: Creates stakeholder-ready architectural decision document  
✅ **Implementation Focus**: Roadmap, success criteria, risk mitigation (not just summary)  
✅ **Professional Format**: Suitable for external communication and project planning  
✅ **Structured Content**: Rich metadata and references for audit trail  
✅ **Proven Pattern**: Uses established 3-tool Scribe approach for reliability

### HAiOS Pattern Benefits

✅ **Evidence-Based**: Every operation creates verifiable file artifacts  
✅ **Durable Context**: All context persisted in files, not ephemeral prompts  
✅ **Separation of Duties**: Clear boundary between orchestrator (metadata) and agent (content)  
✅ **Prevents Hallucination**: Agents cannot modify role names or structure  
✅ **Audit Trail**: Complete traceability of all metadata decisions  
✅ **Testable**: File-based operations enable comprehensive testing

## Tool Logging & Observability - v2.0 ENHANCED

The shared_components.py provides comprehensive validation logging with structured step progression and enhanced observability:

### Sequential Step Validation Pattern
```
Step 1: Reading prompt file...
  [Tool] Read: D:\PROJECTS\haios\agents\2a_agent\A1\A1_PROMPT_FILE_BASED.txt
  [OK] Agent response (1799 chars, 14367ms)
  [VALIDATION] Read-only access validated for: D:\PROJECTS\haios\agents\2a_agent\A1\A1_PROMPT_FILE_BASED.txt
  [VALIDATION] Prompt file read access validated: D:\PROJECTS\haios\agents\2a_agent\A1\A1_PROMPT_FILE_BASED.txt

Step 2: Getting Architect-1 response...
  [VALIDATION] Dialogue skeleton entry created for Architect-1 (round 1)
  [Tool] Read: D:\PROJECTS\haios\agents\2a_agent\output_2A\session_20250717_122748\dialogue.json
  [Tool] Edit: D:\PROJECTS\haios\agents\2a_agent\output_2A\session_20250717_122748\dialogue.json (old: 20 chars, new: 2386 chars)
  [OK] Agent response (1261 chars, 28347ms)
  [DEBUG] Architect-1 used 2 tools: ['Read', 'Edit']
  [VALIDATION] Tool usage validated: Architect-1 used 2 tools correctly
  [COST] Architect-1 operation cost: $0.0826
  [VALIDATION] Architect-1 dialogue update completed successfully
```

### Node-Specific Validation Logs

**ReadPromptNode (Step 1)**:
- `[VALIDATION] Prompt file read access validated: [file_path]`

**UpdateDialogueNode (Step 2)**:
- `[VALIDATION] Dialogue skeleton entry created for [role] (round [X])`
- `[VALIDATION] Tool usage validated: [persona] used X tools correctly`
- `[VALIDATION] [persona] dialogue update completed successfully`

**SummarizerNode (Step 3)**:
- `[VALIDATION] Summary file access validated: [file_path]`
- `[VALIDATION] Dialogue file access validated: [file_path]`
- `[VALIDATION] Tool usage validated: Scribe used X tools correctly`
- `[VALIDATION] Summary generation completed successfully (X chars)`

**ConsensusSynthesisNode (Step 4)**:
- `[VALIDATION] Synthesis skeleton file created: [file_path]`
- `[VALIDATION] Synthesis file access validated: [file_path]`
- `[VALIDATION] Dialogue file access validated: [file_path]`
- `[VALIDATION] Tool usage validated: Synthesis agent used X tools correctly`
- `[VALIDATION] Synthesis generation completed successfully (X chars)`

### Enhanced Performance Metrics
- **Duration Tracking**: All operations timed from start to completion (milliseconds)
- **Character Counts**: Content size metrics for all file operations
- **Cost Tracking**: USD cost tracking for all agent operations (`[COST] operation cost: $X.XXXX`)
- **Tool Validation**: Comprehensive tool usage validation and violation detection
- **Step Progression**: Sequential 1→2→3→4 step numbering across all nodes
- **Operation Completion**: Success/failure validation for all operations

### Validation Hierarchy
1. **File Access Validation**: Confirms file accessibility before operations
2. **Tool Usage Validation**: Validates correct tool count and usage patterns
3. **Operation Completion Validation**: Confirms successful completion with metrics
4. **Cost Tracking**: Monitors operational costs for budget management

### Why Enhanced Logging is Critical
**Production Readiness**: Comprehensive validation logging enables:
- **Real-time Monitoring**: Track operation health and performance
- **Cost Management**: Monitor and optimize operational costs
- **Debugging**: Rapid identification of failures and bottlenecks
- **Compliance**: Audit trail for HAiOS compliance verification
- **Performance Optimization**: Identify and optimize slow operations

### Tool Operation Patterns
- **Read**: `[Tool] Read: path` → `[OK] Agent response (X chars, Yms)`
- **Edit**: `[Tool] Edit: path (old: X chars, new: Y chars)` → `[OK] Agent response (Z chars, Wms)`
- **Write**: `[Tool] Write: path (X chars)` → `[OK] Agent response (Y chars, Zms)`

### Technical Design Notes
**Logging Differences**: Character counts available immediately for Edit/Write (from input parameters) vs Read (from response content after completion) due to Claude Code SDK `ToolUseBlock` structure.

## Tool Security Notes
- Tools marked "Permission Required: Yes" need explicit allowance
- Tools marked "Permission Required: No" are generally safe
- Use principle of least privilege - only grant tools needed for specific tasks