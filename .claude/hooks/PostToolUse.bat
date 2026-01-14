// last updated on: 2025-08-27 13:08:39
@echo off
REM PostToolUse Hook Example - Simple Batch File Version
REM 
REM This is a basic example of a PostToolUse hook using a Windows batch file.
REM This was used for initial testing before implementing the full PowerShell version.
REM 
REM Key learnings from this implementation:
REM 1. PostToolUse hooks receive JSON input via stdin
REM 2. Batch files are limited for JSON parsing - PowerShell is much better
REM 3. Hook configuration format in settings.local.json:
REM    "PostToolUse": [
REM      {
REM        "matcher": "Edit|MultiEdit|Write",
REM        "hooks": [
REM          {
REM            "type": "command", 
REM            "command": ".claude/hooks/PostToolUse.bat"
REM          }
REM        ]
REM      }
REM    ]
REM
REM For production use, see PostToolUse.ps1 which properly parses JSON
REM and adds timestamps to edited files.

echo Hook executed at: %date% %time% >> d:\PROJECTS\peecity\hook-debug.log