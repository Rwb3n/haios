"""
2A Orchestrator Utilities

Helper functions for the PocketFlow-based 2A orchestrator.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def validate_dialogue_file(dialogue_path: str) -> bool:
    """Validate that a dialogue file has the expected structure."""
    try:
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        required_keys = ['metadata', 'adr', 'question', 'dialogue']
        for key in required_keys:
            if key not in data:
                print(f"Missing required key: {key}")
                return False
        
        if not isinstance(data['dialogue'], list):
            print("Dialogue must be a list")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error validating dialogue file: {e}")
        return False


def backup_dialogue_file(dialogue_path: str) -> Optional[str]:
    """Create a backup of the dialogue file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{dialogue_path}.backup_{timestamp}"
        
        import shutil
        shutil.copy2(dialogue_path, backup_path)
        
        return backup_path
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None


def get_dialogue_stats(dialogue_path: str) -> Dict[str, Any]:
    """Get statistics about the dialogue."""
    try:
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        dialogue = data.get('dialogue', [])
        
        stats = {
            'total_entries': len(dialogue),
            'architect1_entries': len([e for e in dialogue if e.get('role') == 'Architect-1']),
            'architect2_entries': len([e for e in dialogue if e.get('role') == 'Architect-2']),
            'rounds_completed': len(set(e.get('round', 0) for e in dialogue if e.get('round', 0) > 0)),
            'status': data.get('metadata', {}).get('status', 'unknown'),
            'created': data.get('metadata', {}).get('created', 'unknown'),
            'consensus_reached': any('**No Further Dissent**' in e.get('content', '') for e in dialogue)
        }
        
        if dialogue:
            stats['last_entry_role'] = dialogue[-1].get('role', 'unknown')
            stats['last_entry_round'] = dialogue[-1].get('round', 0)
        
        return stats
        
    except Exception as e:
        print(f"Error getting dialogue stats: {e}")
        return {}


def clean_old_dialogues(output_dir: str = "output_2A", keep_count: int = 5):
    """Clean up old dialogue files, keeping only the most recent."""
    try:
        output_path = Path(output_dir)
        if not output_path.exists():
            return
        
        # Find all dialogue files
        dialogue_files = list(output_path.glob("dialogue_*.json"))
        
        if len(dialogue_files) <= keep_count:
            return
        
        # Sort by modification time (newest first)
        dialogue_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old files
        for file_path in dialogue_files[keep_count:]:
            file_path.unlink()
            print(f"Removed old dialogue file: {file_path}")
        
    except Exception as e:
        print(f"Error cleaning old dialogues: {e}")


def format_dialogue_for_display(dialogue_path: str) -> str:
    """Format dialogue for human-readable display."""
    try:
        with open(dialogue_path, 'r') as f:
            data = json.load(f)
        
        dialogue = data.get('dialogue', [])
        
        if not dialogue:
            return "No dialogue entries found."
        
        formatted = []
        formatted.append("=== DIALOGUE SUMMARY ===")
        formatted.append(f"Question: {data.get('question', 'Unknown')}")
        formatted.append(f"Total entries: {len(dialogue)}")
        formatted.append("")
        
        for i, entry in enumerate(dialogue, 1):
            role = entry.get('role', 'Unknown')
            round_num = entry.get('round', 0)
            timestamp = entry.get('timestamp', 'Unknown')
            content = entry.get('content', '')
            
            formatted.append(f"Entry {i}: {role} (Round {round_num})")
            formatted.append(f"Time: {timestamp}")
            formatted.append(f"Content: {content[:200]}{'...' if len(content) > 200 else ''}")
            formatted.append("")
        
        return "\n".join(formatted)
        
    except Exception as e:
        return f"Error formatting dialogue: {e}"


def check_file_permissions(file_path: str) -> bool:
    """Check if we have read/write permissions for a file."""
    try:
        # Check if file exists and is readable
        if os.path.exists(file_path):
            if not os.access(file_path, os.R_OK):
                print(f"No read permission for: {file_path}")
                return False
            if not os.access(file_path, os.W_OK):
                print(f"No write permission for: {file_path}")
                return False
        else:
            # Check if we can create the file
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.access(parent_dir, os.W_OK):
                print(f"No write permission for directory: {parent_dir}")
                return False
        
        return True
        
    except Exception as e:
        print(f"Error checking file permissions: {e}")
        return False


def ensure_required_files_exist():
    """Ensure required files and directories exist."""
    required_dirs = ["input_2A", "output_2A", "A1", "A2"]
    required_files = [
        "input_2A/initial_question.txt",
        "A1/A1_PROMPT_FILE_BASED.txt",
        "A2/A2_PROMPT_FILE_BASED.txt"
    ]
    
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Ensured directory exists: {dir_name}")
    
    for file_name in required_files:
        file_path = Path(file_name)
        if not file_path.exists():
            print(f"WARNING: Required file missing: {file_name}")
        else:
            print(f"Found required file: {file_name}")


def extract_speaker_role(prompt_file_path: str) -> str:
    """Extract speaker role from prompt file header."""
    try:
        with open(prompt_file_path, 'r') as f:
            first_line = f.readline().strip()
        
        # Parse <Role Prompt: Description> format
        if first_line.startswith('<') and first_line.endswith('>'):
            # Extract text between < and >
            content = first_line[1:-1]
            
            # Look for "Prompt:" pattern and extract the role part
            if 'Prompt:' in content:
                role_part = content.split('Prompt:')[0].strip()
                return role_part
            else:
                # Fallback: use everything before " Prompt"
                if ' Prompt' in content:
                    return content.split(' Prompt')[0].strip()
                else:
                    return content.strip()
        
        # Fallback: return filename without extension
        return Path(prompt_file_path).stem.replace('_PROMPT_FILE_BASED', '').replace('_', '-')
        
    except Exception as e:
        print(f"Error extracting speaker role from {prompt_file_path}: {e}")
        # Return filename-based fallback
        return Path(prompt_file_path).stem.replace('_PROMPT_FILE_BASED', '').replace('_', '-')


if __name__ == "__main__":
    """Run utilities for testing."""
    print("=== 2A Orchestrator Utilities Test ===")
    
    # Test file checking
    ensure_required_files_exist()
    
    # Test dialogue validation if file exists
    dialogue_path = "output_2A/dialogue_working.json"
    if os.path.exists(dialogue_path):
        print(f"\nValidating dialogue file: {dialogue_path}")
        is_valid = validate_dialogue_file(dialogue_path)
        print(f"Dialogue file valid: {is_valid}")
        
        if is_valid:
            stats = get_dialogue_stats(dialogue_path)
            print(f"Dialogue stats: {stats}")
            
            print("\nFormatted dialogue:")
            print(format_dialogue_for_display(dialogue_path))
    else:
        print(f"Dialogue file not found: {dialogue_path}")