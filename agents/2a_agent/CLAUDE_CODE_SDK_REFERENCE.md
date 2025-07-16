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

### Agent-Specific Tools

#### Architect-1 & Architect-2
- **Tools**: `["Read", "Edit"]`
- **Purpose**: Read dialogue files, edit/append entries
- **Pattern**: Read existing files, make targeted edits
- **Instruction Example**: `"Read dialogue.json then use Edit to append your response"`

#### Scribe (Summarizer) - v2 PROVEN PATTERN
- **Tools**: `["Read", "Edit"]` 
- **Purpose**: Read dialogue data, update summary files
- **Pattern**: Read dialogue.json, read summary.md, edit summary.md
- **Instruction Example**: `"Read dialogue.json then read summary.md then use Edit to update summary"`
- **Tool Count**: MUST use 3 tools (Read dialogue, Read summary, Edit summary)

## Orchestrator Responsibilities - v2 HARDENED PATTERN (HAiOS STANDARD)

### HAiOS Separation of Duties Implementation

- **Skeleton Entry Creation**: Orchestrator ALWAYS pre-creates skeleton entries with role, round, timestamp
- **Agent Content Only**: Agents ONLY fill in the content field of pre-created entries  
- **Metadata Control**: Role names come from prompt file headers, NOT agent hallucination
- **File Operations**: Orchestrator tells agents which files to read/edit
- **Simple Instructions**: "Read file then use Edit to fill content field of last entry"

### HAiOS-Compliant Entry Pattern
```json
// Step 1: Orchestrator creates skeleton BEFORE calling agent
{
  "round": 1,
  "role": "Architect-1",              // Extracted from <Architect-1 Prompt: ...>
  "timestamp": "2025-07-16T18:27:27.123",  // Orchestrator controlled
  "content": ""                       // ONLY field agent can modify
}

// Step 2: Agent receives instruction
"Read dialogue.json then use Edit to fill in the content field of the last entry"

// Step 3: Agent can ONLY modify content, cannot hallucinate metadata
```

### HAiOS Pattern Benefits

✅ **Evidence-Based**: Every operation creates verifiable file artifacts  
✅ **Durable Context**: All context persisted in files, not ephemeral prompts  
✅ **Separation of Duties**: Clear boundary between orchestrator (metadata) and agent (content)  
✅ **Prevents Hallucination**: Agents cannot modify role names or structure  
✅ **Audit Trail**: Complete traceability of all metadata decisions  
✅ **Testable**: File-based operations enable comprehensive testing

## Tool Security Notes
- Tools marked "Permission Required: Yes" need explicit allowance
- Tools marked "Permission Required: No" are generally safe
- Use principle of least privilege - only grant tools needed for specific tasks