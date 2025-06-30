import sys
import os
import re

def lint_file(file_path):
    """
    Lints a clarification file to ensure it conforms to the structured template
    derived from the q3 and q4 examples.
    """
    required_metadata = [
        "**Subject:**",
        "**Status:**",
        "**Decision Date:**",
        "**Participants:**"
    ]
    
    # Using regex to be more flexible with spacing and the '|' character
    # Based on the more structured format of q3.
    required_headings = [
        r"##\s*1\s*.*\s*Clarifying Question",
        r"##\s*2\s*.*\s*Consensus Answer",
        r"##\s*3\s*.*\s*Rationale",
        r"##\s*4\s*.*\s*Implications",
        r"##\s*5\s*.*\s*Alternatives Considered",
        r"##\s*6\s*.*\s*Decision",
        r"##\s*7\s*.*\s*Changelog"
    ]
    
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return 1

    if not content.startswith("# "):
        errors.append("File must start with a level 1 heading (e.g., '# Title').")

    for meta in required_metadata:
        if meta not in content:
            errors.append(f"Missing metadata field: '{meta}'")

    for heading_pattern in required_headings:
        if not re.search(heading_pattern, content, re.IGNORECASE):
            # Clean up pattern for error message
            clean_pattern = heading_pattern.replace(r"\s*", " ").replace(".*", "").replace(r"\\", "")
            errors.append(f"Missing heading matching: '{clean_pattern}'")


    if errors:
        print(f"Linting failed for {os.path.basename(file_path)}:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print(f"Linting successful for {os.path.basename(file_path)}: OK")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lint_clarification_template.py <file1.md> <file2.md> ...")
        sys.exit(1)

    exit_code = 0
    for file_to_lint in sys.argv[1:]:
        if lint_file(file_to_lint) != 0:
            exit_code = 1
    
    sys.exit(exit_code)