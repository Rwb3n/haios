# 2A Agent - Architect Dialogue System

## Overview

The 2A Agent implements the **Architect Dialogue System** - an evaluator-optimizer pattern that transforms vague architectural questions into concrete, implementable technical specifications through structured critical analysis and iterative refinement.

The system uses two AI personas (Architect-1 as evaluator, Architect-2 as optimizer) to engage in structured dialogue, with optional summarization to prevent contextual amnesia in longer conversations.

## Key Features

- **File-based dialogue persistence** - All conversations stored in JSON format
- **Configurable round limits** - Support for fixed rounds or infinite dialogue (-1)
- **Dual-mode consensus detection** - Boolean field (primary) + pattern matching (fallback)
- **Context summarization** - Optional Scribe persona prevents dialogue amnesia (v1.1)
- **PocketFlow integration** - Built on minimalist async LLM framework
- **Atomic node architecture** - Modular design with one class per file

## Architecture

The system has been refactored from a monolithic script into a **file-based dialogue system** using clean PocketFlow patterns:

### File-Based Dialogue Pattern

**Core Concept**: Both agents read from and append to the same JSON dialogue file (`dialogue_working.json`) which serves as the persistent shared state across rounds.

```
Round 1: A1 reads file → appends response → A2 reads file → appends response
Round 2: A1 reads file → appends response → A2 reads file → appends response
...until consensus or max rounds
```

### Core Components

```
2a_agent/
├── main_clean.py               # Entry point with CLI support
├── flow_clean.py               # PocketFlow graph definitions
├── nodes/                      # Atomic node implementations (v1.1)
│   ├── __init__.py            # Public API
│   ├── architect1_node.py      # Evaluator persona
│   ├── architect2_node.py      # Optimizer persona  
│   ├── consensus_check_node.py # Round control
│   ├── summarizer_node.py      # Scribe context (v1.1)
│   ├── dialogue_summary_node.py # Final display
│   └── shared_components.py    # Common utilities
├── A1/                         # Architect-1 prompts
├── A2/                         # Architect-2 prompts
├── Scribe/                     # Summarizer prompts (v1.1)
├── input_2A/                   # Input questions
├── output_2A/                  # Dialogue outputs
├── session_config.json         # Example configuration
├── __legacy/                   # Historical implementations
└── __backup/                   # Version backups
```

### PocketFlow Compliance

The clean implementation follows all PocketFlow best practices:

✅ **No exception handling in exec() methods** - Uses Node's built-in retry mechanism  
✅ **exec() methods don't access shared store** - Clean separation of concerns  
✅ **Proper retry mechanisms** - `max_retries=3, wait=1.0` with graceful fallbacks  
✅ **Action-based routing** - "continue", "consensus", "error" drive flow  
✅ **Async throughout** - Proper AsyncNode usage for Claude SDK  

## Usage

### Basic Run
```bash
python main_clean.py
```

### With Configuration File
```bash
python main_clean.py --config session_config.json
```

### Custom Parameters
```bash
python main_clean.py --adr docs/ADR/ADR-OS-001.md --question "What about timeouts?" --max-rounds 5
```

## Configuration

### Session Config (session_config.json)
```json
{
  "session_id": "session_20250716_122308",
  "adr_path": "../../docs/ADR/ADR-OS-001.md",
  "question_path": "input_2A/initial_question.txt",
  "output_dir": "output_2A/session_20250716_122308",
  "max_rounds": -1,  // -1 for infinite rounds
  "personas": {
    "architect_1": {"prompt_path": "A1/A1_PROMPT_FILE_BASED.txt"},
    "architect_2": {"prompt_path": "A2/A2_PROMPT_FILE_BASED.txt"}
  }
}
```

### Required Files
- `input_2A/initial_question.txt`: Initial question for the dialogue
- `A1/A1_PROMPT_FILE_BASED.txt`: Architect-1 prompt
- `A2/A2_PROMPT_FILE_BASED.txt`: Architect-2 prompt
- `Scribe/Scribe_PROMPT.txt`: Summarizer prompt (v1.1)

### Output
- `output_2A/dialogue_working.json`: Dialogue state and results

## Flow Diagram (v1.4 - Current Atomic Pattern)

```
[ConsensusCheck] ─(continue)→ [SummarizerNode] → [ReadPrompt_A1] → [UpdateDialogue_A1]
       ↑                                                                     ↓
       │                                           [ReadPrompt_A2] ← ────────┘
       │                                                  ↓
       └────────────────(continue)─────────── [UpdateDialogue_A2]
       │
    (consensus)
       ↓
[ConsensusSynthesis] → END
```

### Active Node Structure (v1.4)

```
ConsensusCheckNode 
    ├─ "continue" → SummarizerNode
    └─ "consensus" → ConsensusSynthesisNode

SummarizerNode
    └─ "default" → ReadPromptNode(A1)

ReadPromptNode(A1) 
    ├─ "default" → UpdateDialogueNode(Architect-1)
    └─ "error" → ConsensusSynthesisNode

UpdateDialogueNode(Architect-1)
    ├─ "continue" → ReadPromptNode(A2)
    └─ "error" → ConsensusSynthesisNode

ReadPromptNode(A2)
    ├─ "default" → UpdateDialogueNode(Architect-2) 
    └─ "error" → ConsensusSynthesisNode

UpdateDialogueNode(Architect-2)
    ├─ "continue" → ConsensusCheckNode (loop)
    ├─ "consensus" → ConsensusSynthesisNode
    └─ "error" → ConsensusSynthesisNode

ConsensusSynthesisNode
    └─ "default" → END
```

### Legacy Nodes (Deprecated - v1.3)

Legacy monolithic nodes moved to `nodes/__legacy/`:
- `Architect1Node` → Replaced by ReadPromptNode + UpdateDialogueNode atomic chain
- `Architect2Node` → Replaced by ReadPromptNode + UpdateDialogueNode atomic chain  
- `DialogueSummaryNode` → Replaced by ConsensusSynthesisNode (professional deliverable)

## Key Improvements

### From Monolithic to Modular (v1.2)
- **Before**: Single 216-line script with complex while loop
- **After**: Modular nodes with clear responsibilities

### PocketFlow Compliance (v1.2)
- **Before**: Manual exception handling and state management
- **After**: Built-in retry mechanisms and graceful fallbacks

### File-Based State Management (v1.2)
- **Before**: Complex in-memory state coordination
- **After**: Simple, persistent JSON file shared between agents

### Atomic Execution Pattern (v1.3)
- **Before**: Multi-step orchestration within single nodes (AP-007 anti-pattern)
- **After**: Truly atomic nodes - ReadPromptNode + UpdateDialogueNode chains
- **Result**: Perfect PocketFlow compliance and enhanced retry logic

### Enhanced Consensus Detection (v1.3)
- **Before**: Hardcoded pattern matching for "**No Further Dissent**"
- **After**: Dual-mode approach with boolean field (primary) + pattern matching (fallback)
- **Benefits**: Explicit control signals, backwards compatibility, language-agnostic

### Fixed Round Logic (Bug Fix)
- **Before**: Infinite loop bug - script would run indefinitely without respecting round limits
- **After**: Proper round counting and max_rounds enforcement
- **Result**: Each round produces exactly 2 dialogue entries (1 per agent)
- **Termination**: Script properly stops after max_rounds or consensus detection

### Fixed Consensus Detection Logic (v1.3.1 Bug Fix)
- **Before**: Consensus only detected after Architect-2 responses, missing Architect-1 consensus signals
- **After**: Either architect can signal consensus via boolean field or pattern matching
- **Result**: Immediate dialogue termination when any architect sets `consensus: true`
- **Enhancement**: Improved logging shows which architect signaled consensus

### Consensus Synthesis Engine (v1.4) - SDK Reference Compliant
- **Added**: ConsensusSynthesisNode following proven Scribe pattern from SDK Reference
- **Trigger**: Automatically invoked when consensus achieved (any architect sets `consensus: true`)
- **Pattern**: 3-tool approach - Read dialogue → Read skeleton → Edit synthesis
- **Tools**: `["Read", "Edit"]` (SDK Reference file modification pattern)
- **Process**:
  1. **Orchestrator**: Creates structured skeleton with metadata from dialogue.json
  2. **Agent**: Reads dialogue context and fills skeleton placeholders
  3. **Output**: Professional `consensus_synthesis.md` for stakeholder communication
- **vs SummarizerNode**: SummarizerNode tracks ongoing dialogue, ConsensusSynthesisNode creates final deliverable
- **Content**: Implementation roadmap, success criteria, risk mitigation (not just summary)
- **Fallback**: Creates basic skeleton if dialogue reading fails

### Node Structure Cleanup (v1.4)
- **Added**: Clean separation between active and deprecated nodes
- **Active Nodes**: Only SDK Reference compliant, atomic pattern nodes in main directory
- **Legacy Nodes**: Deprecated monolithic nodes moved to `nodes/__legacy/`
- **Import Structure**: Clean imports with legacy nodes accessible via `__legacy/` path
- **Backward Compatibility**: Test flows still work via legacy imports

### Enhanced Testability
- **Before**: Hard to test individual components
- **After**: Each atomic node can be tested independently
- **Structure**: Clean node directory with only active components

### Improved Maintainability
- **Before**: Monolithic script hard to modify
- **After**: Easy to modify individual nodes or flow structure
- **Clean Architecture**: Deprecated code isolated in legacy directory

## Current Node Architecture (v1.4)

### Active Nodes (Main Directory)
```
nodes/
├── consensus_check_node.py       # Flow control and consensus detection
├── consensus_synthesis_node.py   # Professional deliverable generation
├── read_prompt_node.py           # Atomic: read prompt files
├── update_dialogue_node.py       # Atomic: update dialogue with agent responses  
├── summarizer_node.py            # Ongoing dialogue tracking
└── shared_components.py          # Common utilities
```

### Legacy Nodes (Deprecated)
```
nodes/__legacy/
├── architect1_node.py            # Replaced by atomic chain
├── architect2_node.py            # Replaced by atomic chain
├── dialogue_summary_node.py     # Replaced by ConsensusSynthesisNode
└── ... (other legacy files)
```

## Migration from Legacy

The legacy monolithic approach has been replaced with atomic, SDK Reference compliant patterns:

1. **Initialization** → `create_dialogue_file()` in `main_clean.py`
2. **Agent Steps** → Atomic ReadPromptNode + UpdateDialogueNode chains
3. **Main Loop** → Flow graph in `flow_clean.py` using active nodes only
4. **Consensus Detection** → Dual-mode detection in `UpdateDialogueNode` 
5. **Final Deliverable** → `ConsensusSynthesisNode` (replaces basic summary)

## Customization

### Adding New Node Types

```python
from pocketflow import AsyncNode

class CustomNode(AsyncNode):
    def __init__(self):
        super().__init__(max_retries=3, wait=1.0)
    
    async def prep_async(self, shared):
        # Prepare data from shared state
        return context
    
    async def exec_async(self, context):
        # Execute main logic (NO shared access, NO exception handling)
        return result
    
    async def exec_fallback_async(self, prep_res, exc):
        # Graceful fallback on failure
        return fallback_result
    
    async def post_async(self, shared, prep_res, exec_res):
        # Update shared state and return action
        return "next_action"
```

### Creating New Flows

```python
from flow_clean import create_custom_flow

# Create flow with custom parameters
custom_flow = create_custom_flow(
    a1_prompt="custom_prompts/A1_CUSTOM.txt",
    a2_prompt="custom_prompts/A2_CUSTOM.txt"
)
```

### Extending the Graph

```python
from pocketflow import AsyncFlow
from nodes_clean import Architect1Node, Architect2Node

def create_extended_flow():
    # Add new nodes
    validator = ValidationNode()
    
    # Modify graph structure
    architect1 = Architect1Node()
    architect2 = Architect2Node()
    
    architect1 - "default" >> validator
    validator - "approved" >> architect2
    validator - "rejected" >> architect1
    
    return AsyncFlow(start=architect1)
```

## Development

### Running Tests
```bash
# Test single round
python test_single_round.py

# Test with configuration
python main_clean.py --config test_configs/infinite_rounds.json
```

### Debug Output
The system provides comprehensive validation logging with structured step progression:
- Sequential step numbering (1→2→3→4)
- File access validation
- Tool usage validation  
- Cost tracking
- Operation completion validation
- Round progression
- Consensus detection

### Example Debug Session
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

Step 3: Generating dialogue summary (Round 2)...
  [VALIDATION] Summary file access validated: [file_path]
  [VALIDATION] Dialogue file access validated: [file_path]
  [Tool] Read: [dialogue file]
  [Tool] Read: [summary file]
  [Tool] Edit: [summary file] (old: 297 chars, new: 2618 chars)
  [OK] Agent response (1007 chars, 33848ms)
  [DEBUG] Scribe used 3 tools: ['Read', 'Read', 'Edit']
  [VALIDATION] Tool usage validated: Scribe used 3 tools correctly
  [COST] Scribe operation cost: $0.0777
  [VALIDATION] Summary generation completed successfully (1007 chars)

Step 4: Creating consensus synthesis...
  [VALIDATION] Synthesis skeleton file created: [file_path]
  [VALIDATION] Synthesis file access validated: [file_path]
  [VALIDATION] Dialogue file access validated: [file_path]
  [Tool] Read: [dialogue file]
  [Tool] Read: [synthesis file]
  [Tool] Edit: [synthesis file] (multiple edits)
  [OK] Agent response (1487 chars, 92639ms)
  [DEBUG] Synthesis agent used 8 tools: ['Read', 'Read', 'Edit', 'Edit', 'Edit', 'Edit', 'Edit', 'Edit']
  [VALIDATION] Tool usage validated: Synthesis agent used 8 tools correctly
  [COST] Synthesis operation cost: $0.1903
  [VALIDATION] Synthesis generation completed successfully (1487 chars)

================================================================================
🎯 CONSENSUS SYNTHESIS COMPLETE
================================================================================
📝 Synthesis saved: output_2A/session_20250717_122748\consensus_synthesis.md
📊 Length: 11857 characters
================================================================================
```

## HAiOS Compliance & Design Patterns

The 2A Agent implements **HAiOS-compliant patterns** that prevent agent hallucination and ensure metadata control:

### Claude Code SDK v2 Pattern (HARDENED)

**Core Principle**: NO CONTENT EMBEDDING IN PROMPTS

✅ **Orchestrator Pre-fills Skeleton Entries**
```json
// Orchestrator creates this BEFORE calling agent:
{
  "round": 1,
  "role": "Architect-1",           // Role extracted from prompt file header
  "timestamp": "2025-07-16T18:27:27.123",
  "content": ""                    // Agent ONLY fills this field
}
```

✅ **Agent Instructions are File Operations Only**
```
"Read dialogue.json then use Edit to fill in the content field of the last entry"
```

✅ **Role Name Control**
- Role names extracted from prompt file headers: `<Architect-1 Prompt: The Proposer>`
- Orchestrator controls all metadata (role, round, timestamp)
- Agents cannot hallucinate role names or modify structure

### HAiOS Three Pillars Implementation

1. **Evidence-Based Development**: All dialogue entries are persisted JSON artifacts
2. **Durable, Co-located Context**: Context lives in files, not embedded in prompts  
3. **Separation of Duties**: Orchestrator handles metadata, agents handle content only

### Pattern Benefits

- **Prevents Agent Hallucination**: Agents cannot modify role names or structure
- **Ensures Consistency**: All entries follow identical JSON schema
- **Maintains Audit Trail**: Complete metadata control with HAiOS standards
- **Enables Testing**: File-based operations are easily testable and reproducible

### Observability & Performance Metrics

The 2A Agent provides comprehensive validation logging with structured step progression:

**Sequential Step Validation:**
- **Step 1**: ReadPromptNode - File access validation
- **Step 2**: UpdateDialogueNode - Skeleton creation, tool usage, completion validation
- **Step 3**: SummarizerNode - File access, tool usage, content validation
- **Step 4**: ConsensusSynthesisNode - Skeleton creation, file access, tool usage, completion validation

**Validation Log Types:**
- `[VALIDATION] File access validated: [file_path]` - File accessibility confirmation
- `[VALIDATION] Tool usage validated: [agent] used X tools correctly` - Tool usage compliance
- `[VALIDATION] [Operation] completed successfully (X chars)` - Operation completion confirmation
- `[VALIDATION] [Specific operation] created/updated: [details]` - Specific operation validation

**Enhanced Observability:**
- **Duration Tracking**: All operations timed from start to completion (milliseconds)
- **Character Counts**: Content size metrics for all file operations
- **Cost Tracking**: USD cost tracking for all agent operations
- **Tool Validation**: Comprehensive tool usage validation and violation detection
- **Performance Metrics**: Response times, content sizes, tool efficiency

**Logging Patterns by Tool Type:**
- **Read**: `[Tool] Read: path` → `[OK] Agent response (X chars, Yms)`
- **Edit**: `[Tool] Edit: path (old: X chars, new: Y chars)` → `[OK] Agent response (Z chars, Wms)`
- **Write**: `[Tool] Write: path (X chars)` → `[OK] Agent response (Y chars, Zms)`

**Technical Design**: Logging differences reflect Claude Code SDK constraints - Edit/Write show immediate character counts from input parameters, while Read operations show counts only after completion due to content being in the response rather than input.

## Integration with HAIOS

The 2A Agent serves as a critical component in HAIOS's architecture validation:
- Transforms architectural gaps into concrete specifications
- Provides structured critical analysis for ADR refinement  
- Enables automated clarification processing
- Supports the "Certainty Ratchet" by moving from ambiguity to verified truth
- **Implements HAiOS-compliant agent orchestration patterns**

## Future Enhancements

### Immediate Priority: Hook System Implementation

**CRITICAL_INITIATIVE**: Architectural Hardening via Hook Validation Nodes

**Background**: HAiOS feedback identified "Benevolent Misalignment" as a critical failure mode where Claude Code agents helpfully refactor code while inadvertently destroying carefully-designed architectural patterns. This represents an existential threat to the "Certainty Ratchet" philosophy.

**Current Gap**: Claude Code SDK v0.0.14 lacks hook support that exists in the CLI, making SDK-level tool interception impossible.

**Proposed Solution**: PocketFlow Hook Validation Nodes

#### **Implementation Plan: Hook Node Architecture**

**Phase 1: Pattern Validation Nodes**
- [ ] **PreValidationHookNode** - Validates inputs before expensive operations
  - File accessibility validation
  - Parameter compliance checking
  - Business rule enforcement
- [ ] **PostValidationHookNode** - Validates outputs after operations
  - Content quality validation
  - Format compliance checking
  - Rollback trigger mechanisms

**Phase 2: Architectural Pattern Protection**
- [ ] **PocketFlowPatternValidator** - Ensures node compliance
  - Validates AsyncNode inheritance patterns
  - Enforces prep→exec→post structure
  - Checks atomic operation principles
- [ ] **HAiOSPatternValidator** - Ensures HAiOS compliance
  - Validates skeleton creation patterns
  - Enforces separation of duties
  - Checks file-based operation patterns

**Phase 3: Integration & Flow Enhancement**
```
[Node] → [PreHook] → [Operation] → [PostHook] → [NextNode]
           ↓                          ↓
    [ValidationError]         [QualityCheck/Rollback]
```

**Benefits**:
- **Defense in Depth**: Workflow-level protection complementing future SDK-level hooks
- **Immediate Implementation**: No dependency on SDK hook support
- **Pattern Enforcement**: Deterministic validation of architectural patterns
- **Rollback Capability**: Safe recovery from validation failures

#### **Technical Specifications**

**Hook Node Base Class**:
```python
class BaseHookNode(AsyncNode):
    def __init__(self, validation_rules: List[ValidationRule]):
        super().__init__(max_retries=1, wait=0)
        self.validation_rules = validation_rules
    
    async def exec_async(self, context) -> ValidationResult:
        # Run validation rules
        # Return PASS/FAIL with detailed feedback
```

**Validation Rule Engine**:
- **Pattern Matching Rules**: Regex-based pattern validation
- **Structural Rules**: JSON schema validation
- **Business Logic Rules**: Custom validation functions
- **Performance Rules**: Size/duration threshold validation

### Standard Enhancements

- [ ] Web UI for dialogue visualization
- [ ] Integration with n8n workflows
- [ ] Support for multi-ADR analysis
- [ ] Batch question processing
- [ ] Dialogue analytics and metrics
- [ ] Real-time streaming output
- [ ] Export to multiple formats (Markdown, PDF)
- [ ] Integration with Plan Validation Gateway