# Deep Detail: Governance Hook Dispatcher

```text
┌─────────────────────────────────────────────────────────────┐
│                       CLAUDE CODE CLI                       │
│  (Configured via .claude/settings.local.json hooks block)   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                      [JSON Payload]
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│          hook_dispatcher.py (Single Entry Point)            │
│                 Reads stdin, parses JSON                    │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
       (Event Name?)   (Event Name?)   (Event Name?)
              │               │               │
┌─────────────▼──┐ ┌──────────▼─────┐ ┌───────▼────────┐
│UserPromptSubmit│ │   PreToolUse   │ │  PostToolUse / │
│                │ │                │ │     Stop       │
├────────────────┤ ├────────────────┤ ├────────────────┤
│ user_prompt_   │ │ pre_tool_      │ │ post_tool_     │
│ submit.py      │ │ use.py         │ │ use.py /       │
│                │ │                │ │ stop.py        │
├────────────────┤ ├────────────────┤ ├────────────────┤
│ Yields:        │ │ Yields:        │ │ Yields:        │
│ Text injection │ │ JSON decisions │ │ Side effects   │
│ (vitals, etc)  │ │ (block/allow)  │ │ (Extraction)   │
└─────────────┬──┘ └──────────┬─────┘ └───────┬────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                       [Outputs stdout]
                              │
                              v
┌─────────────────────────────────────────────────────────────┐
│                       CLAUDE CODE CLI                       │
│    (Executes modified prompt or blocks tool execution)      │
└─────────────────────────────────────────────────────────────┘
```

## Description
The `hook_dispatcher.py` script is the exact physical nexus of the HAIOS Governance system. It entirely replaces older PowerShell implementations.
- **Input**: Reads JSON directly from `stdin` provided by Claude Code.
- **Routing**: Imports the precise python module matching the `hook_event_name`.
- **Outputs**: For `UserPromptSubmit`, it prints plain text that gets prepended to the user's prompt (injecting system vitals and status). For `PreToolUse`, it prints JSON containing `{ "permissionDecision": "allow" | "block" }`.
