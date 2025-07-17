"""
2A Orchestrator Main - Clean PocketFlow Implementation

Simplified main script that preserves the exact file-based dialogue pattern.
Each agent reads from and appends to the same dialogue JSON file.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import anyio

from flow_clean import create_2a_flow, create_single_round_flow


def create_dialogue_file(adr_path: str = "../../docs/ADR/ADR-OS-001.md", 
                        question_path: str = "input_2A/initial_question.txt",
                        max_rounds: int = 3,
                        session_dir: str = None) -> tuple[str, str]:
    """
    Create initial dialogue file and session directory.
    
    Returns tuple of (dialogue_path, session_dir)
    """
    print(f"Loading ADR from: {adr_path}")
    with open(adr_path, 'r') as f:
        adr = f.read()
    
    print(f"Loading question from: {question_path}")
    with open(question_path, 'r') as f:
        question = f.read().strip()
    
    # Create session directory if not provided
    if session_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = f"output_2A/session_{timestamp}"
    
    Path(session_dir).mkdir(parents=True, exist_ok=True)
    
    dialogue_data = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "status": "in_progress", 
            "max_rounds": max_rounds
        },
        "adr": adr,
        "question": question,
        "dialogue": []
    }
    
    dialogue_path = f"{session_dir}/dialogue.json"
    
    with open(dialogue_path, 'w') as f:
        json.dump(dialogue_data, f, indent=2)
    
    # Pre-create summary.md structure (like dialogue.json)
    summary_path = f"{session_dir}/summary.md"
    initial_summary = """# Dialogue Summary: [TO BE UPDATED]

**Question**: [TO BE EXTRACTED]
**Round**: [TO BE UPDATED]
**Status**: IN_PROGRESS

## Key Decisions & Agreements
[TO BE FILLED]

## Open Questions & Dissents
[TO BE FILLED]

## Current State of Proposal
[TO BE FILLED]

## Context for Next Round
[TO BE FILLED]"""
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(initial_summary)
    
    print(f"Created dialogue file: {dialogue_path}")
    print(f"Created summary file: {summary_path}")
    print(f"Question: {question}")
    return dialogue_path, session_dir


async def run_2a_orchestrator(adr_path: str, question_path: str, max_rounds: int):
    """
    Run the 2A orchestrator with clean PocketFlow implementation.
    
    File-based pattern: Both agents read from and append to the same dialogue file.
    """
    print("=== 2A Orchestrator (Clean PocketFlow) ===\n")
    
    # Setup dialogue file and session directory
    dialogue_path, session_dir = create_dialogue_file(adr_path, question_path, max_rounds)
    
    # Initialize session tracking
    session_id = session_dir.split('/')[-1]  # Extract session_id from path
    # session_metrics = init_session_tracking(session_id)
    
    # Create flow
    dialogue_flow = create_2a_flow()
    
    # Run rounds with proper file-based state management
    shared = {
        "round_num": 1,
        "dialogue_path": dialogue_path,
        "session_dir": session_dir,
        "max_rounds": max_rounds
        # "session_metrics": session_metrics,
        # "current_round_metrics": None  # Will be initialized by consensus check
    }
    
    # Run the flow until completion
    try:
        result = await dialogue_flow.run_async(shared)
        
        if result == "error":
            print(f"\nOrchestration stopped: Agent failed")
            # session_metrics.final_status = "error"
        elif result == "consensus":
            print(f"\nConsensus reached")
            # session_metrics.final_status = "consensus"
        else:
            print(f"\nDialogue completed")
            # session_metrics.final_status = "max_rounds"
            
    except Exception as e:
        print(f"\nOrchestration failed: {e}")
        # session_metrics.final_status = "error"
    
    # Generate final session summary
    # print(generate_session_summary(session_metrics))
    
    # Update final dialogue metadata
    try:
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        data["metadata"]["status"] = "completed"
        data["metadata"]["completed"] = datetime.now().isoformat()
        
        with open(dialogue_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Warning: Failed to update dialogue metadata: {e}")
    
    return True


async def run_single_round_test():
    """Run a single round test for debugging."""
    print("=== Single Round Test ===\n")
    
    # Create minimal dialogue file
    dialogue_path, session_dir = create_dialogue_file(max_rounds=1)
    
    shared = {
        "dialogue_path": dialogue_path,
        "session_dir": session_dir,
        "round_num": 1,
        "max_rounds": 1
    }
    
    # Create and run single round flow
    test_flow = create_single_round_flow()
    
    try:
        result = await test_flow.run_async(shared)
        print(f"\nSingle round test completed: {result}")
        return True
    except Exception as e:
        print(f"\nSingle round test failed: {e}")
        return False


async def main(adr_path=None, question_path=None, max_rounds=None):
    """Main orchestration function."""
    print("=== Working 2A Orchestrator ===\n")
    
    # Configuration - use parameters if provided, otherwise use defaults
    if adr_path is None:
        adr_path = sys.argv[1] if len(sys.argv) > 1 else "../../docs/ADR/ADR-OS-001.md"
    if question_path is None:
        question_path = sys.argv[2] if len(sys.argv) > 2 else "input_2A/initial_question.txt"
    if max_rounds is None:
        max_rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    print(f"Configuration:")
    print(f"  ADR path: {adr_path}")
    print(f"  Question path: {question_path}")
    print(f"  Max rounds: {max_rounds}")
    print()
    
    # Run the orchestrator
    success = await run_2a_orchestrator(adr_path, question_path, max_rounds)
    
    return 0 if success else 1


if __name__ == "__main__":
    # Print usage if help requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python main_clean.py [ADR_PATH] [QUESTION_PATH] [MAX_ROUNDS]")
        print("       python main_clean.py --config SESSION_CONFIG.json")
        print()
        print("Arguments:")
        print("  ADR_PATH      Path to ADR file (default: ../../docs/ADR/ADR-OS-001.md)")
        print("  QUESTION_PATH Path to question file (default: input_2A/initial_question.txt)")
        print("  MAX_ROUNDS    Maximum dialogue rounds (default: 3)")
        print()
        print("Session Config:")
        print("  --config FILE Use JSON session config file")
        print()
        print("Examples:")
        print("  python main_clean.py")
        print("  python main_clean.py ../../docs/ADR/ADR-OS-020.md")
        print("  python main_clean.py ../../docs/ADR/ADR-OS-020.md input_2A/security_question.txt 5")
        print("  python main_clean.py --config session_config.json")
        print()
        print("Test mode:")
        print("  python main_clean.py --test")
        sys.exit(0)
    
    # Special test mode
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        result = anyio.run(run_single_round_test)
        sys.exit(0 if result else 1)
    
    # Session config mode
    if len(sys.argv) > 2 and sys.argv[1] == '--config':
        config_path = sys.argv[2]
        
        # Load session config
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            adr_path = config['adr_path']
            question_path = config['question_path']
            max_rounds = config['max_rounds']
            output_dir = config.get('output_dir', 'output_2A')
            
            # Create session output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            print(f"Running session: {config['session_id']}")
            print(f"Output directory: {output_dir}")
            
            # Run with session config
            exit_code = anyio.run(main, adr_path, question_path, max_rounds)
            sys.exit(exit_code)
            
        except Exception as e:
            print(f"Error loading session config: {e}")
            sys.exit(1)
    
    # Normal execution
    exit_code = anyio.run(main)
    sys.exit(exit_code)