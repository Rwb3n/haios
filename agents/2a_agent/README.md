# 2A Agent - Architect Dialogue System

## Overview

The 2A Agent implements the **Architect Dialogue System** - an evaluator-optimizer pattern that transforms vague architectural questions into concrete, implementable technical specifications through structured critical analysis and iterative refinement.

The system uses two AI personas (Architect-1 as evaluator, Architect-2 as optimizer) to engage in structured dialogue, with optional summarization to prevent contextual amnesia in longer conversations.

## Key Features

- **File-based dialogue persistence** - All conversations stored in JSON format
- **Configurable round limits** - Support for fixed rounds or infinite dialogue (-1)
- **Consensus detection** - Automatic termination when "**No Further Dissent**" is detected
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

## Flow Diagram (v1.1)

```
[ConsensusCheck] ─(continue)→ [SummarizerNode] → [Architect1] → [Architect2]
       ↑                                                              │
       └────────────────(continue)────────────────────────────────────┘
       │
    (consensus)
       ↓
[DialogueSummary] → END
```

### Flow Details

```
ConsensusCheckNode 
    ├─ "continue" → SummarizerNode (v1.1)
    └─ "consensus" → DialogueSummaryNode

SummarizerNode (v1.1)
    └─ "default" → Architect1Node

Architect1Node
    ├─ "default" → Architect2Node
    └─ "error" → DialogueSummaryNode

Architect2Node
    ├─ "continue" → ConsensusCheckNode (loop)
    ├─ "consensus" → DialogueSummaryNode
    └─ "error" → DialogueSummaryNode

DialogueSummaryNode
    └─ "default" → END
```

## Key Improvements

### From Monolithic to Modular
- **Before**: Single 216-line script with complex while loop
- **After**: Modular nodes with clear responsibilities

### PocketFlow Compliance
- **Before**: Manual exception handling and state management
- **After**: Built-in retry mechanisms and graceful fallbacks

### File-Based State Management
- **Before**: Complex in-memory state coordination
- **After**: Simple, persistent JSON file shared between agents

### Enhanced Testability
- **Before**: Hard to test individual components
- **After**: Each node can be tested independently

### Improved Maintainability
- **Before**: Monolithic script hard to modify
- **After**: Easy to modify individual nodes or flow structure

### Fixed Round Logic (Bug Fix)
- **Before**: Infinite loop bug - script would run indefinitely without respecting round limits
- **After**: Proper round counting and max_rounds enforcement
- **Result**: Each round produces exactly 2 dialogue entries (1 per agent)
- **Termination**: Script properly stops after max_rounds or consensus detection

## Migration from Legacy

The legacy `2a_orchestrator_working.py` has been replaced with this clean system:

1. **Initialization** → `create_dialogue_file()` in `main_clean.py`
2. **Agent Steps** → `Architect1Node` and `Architect2Node` in `nodes_clean.py`
3. **Main Loop** → Flow graph in `flow_clean.py`
4. **Consensus Detection** → `ConsensusCheckNode` and logic in `Architect2Node`
5. **Summary** → `DialogueSummaryNode`

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
The system provides detailed console output:
- Node execution status
- Tool usage tracking
- Dialogue summary content (with debug logging enabled)
- Round progression
- Consensus detection

### Example Debug Session
```
--- Generating Dialogue Summary (Round 2) ---
  [Tool] Read: D:\PROJECTS\haios\agents\2a_agent\Scribe\Scribe_PROMPT.txt
  [OK] Generated dialogue summary (1702 chars)
  [OK] Dialogue summary stored in shared state

============================================================
DIALOGUE SUMMARY CONTENT:
============================================================
[Summary content appears here]
============================================================
END DIALOGUE SUMMARY
============================================================
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

## Integration with HAIOS

The 2A Agent serves as a critical component in HAIOS's architecture validation:
- Transforms architectural gaps into concrete specifications
- Provides structured critical analysis for ADR refinement  
- Enables automated clarification processing
- Supports the "Certainty Ratchet" by moving from ambiguity to verified truth
- **Implements HAiOS-compliant agent orchestration patterns**

## Future Enhancements

- [ ] Web UI for dialogue visualization
- [ ] Integration with n8n workflows
- [ ] Support for multi-ADR analysis
- [ ] Batch question processing
- [ ] Dialogue analytics and metrics
- [ ] Real-time streaming output
- [ ] Export to multiple formats (Markdown, PDF)
- [ ] Integration with Plan Validation Gateway