#!/usr/bin/env python3
"""
Diagram Compliance Checker for HAIOS ADR Canon

This script parses all ADRs looking for NON-COMPLIANCE statements regarding
missing diagrams and validates that required diagrams are present.

Part of: EXEC_PLAN_AUTOMATE_ADR_HYGIENE_V1
Addresses: ADR drift risk from missing required diagrams
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


def find_noncompliance_statements(content: str) -> List[Dict[str, Any]]:
    """Find NON-COMPLIANCE statements in ADR content."""
    statements = []
    
    # Pattern to match NON-COMPLIANCE statements
    pattern = r'NON-COMPLIANCE:\s*([^.]+\.)'
    matches = re.finditer(pattern, content, re.IGNORECASE)
    
    for match in matches:
        statement = match.group(1).strip()
        statements.append({
            'full_text': match.group(0),
            'statement': statement,
            'start_pos': match.start(),
            'end_pos': match.end(),
            'line_context': content[max(0, match.start()-100):match.end()+100]
        })
    
    return statements


def find_diagrams(content: str) -> List[Dict[str, Any]]:
    """Find existing diagrams in the content."""
    diagrams = []
    
    # Pattern 1: Mermaid diagrams
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    mermaid_matches = re.finditer(mermaid_pattern, content, re.DOTALL)
    
    for match in mermaid_matches:
        diagram_content = match.group(1).strip()
        diagram_type = 'unknown'
        
        # Determine diagram type from content
        if 'stateDiagram' in diagram_content or 'state ' in diagram_content:
            diagram_type = 'state_machine'
        elif 'graph' in diagram_content or 'flowchart' in diagram_content:
            diagram_type = 'flowchart'
        elif 'sequenceDiagram' in diagram_content:
            diagram_type = 'sequence'
        elif 'classDiagram' in diagram_content:
            diagram_type = 'class'
        
        diagrams.append({
            'type': 'mermaid',
            'diagram_type': diagram_type,
            'content': diagram_content,
            'start_pos': match.start(),
            'end_pos': match.end()
        })
    
    # Pattern 2: PlantUML diagrams
    plantuml_pattern = r'```plantuml\s*\n(.*?)\n```'
    plantuml_matches = re.finditer(plantuml_pattern, content, re.DOTALL)
    
    for match in plantuml_matches:
        diagrams.append({
            'type': 'plantuml',
            'diagram_type': 'unknown',
            'content': match.group(1).strip(),
            'start_pos': match.start(),
            'end_pos': match.end()
        })
    
    # Pattern 3: Image references
    image_pattern = r'!\[([^\]]*)\]\(([^)]+\.(png|jpg|jpeg|svg|gif))\)'
    image_matches = re.finditer(image_pattern, content)
    
    for match in image_matches:
        alt_text = match.group(1)
        image_path = match.group(2)
        
        diagrams.append({
            'type': 'image',
            'diagram_type': 'image',
            'alt_text': alt_text,
            'path': image_path,
            'start_pos': match.start(),
            'end_pos': match.end()
        })
    
    return diagrams


def analyze_compliance_requirements(noncompliance_statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze NON-COMPLIANCE statements to determine required diagrams."""
    requirements = []
    
    for statement in noncompliance_statements:
        statement_text = statement['statement'].lower()
        
        required_diagram = {
            'statement': statement,
            'required_type': 'unknown',
            'description': statement['statement']
        }
        
        # Determine required diagram type from statement
        if 'state machine' in statement_text or 'state diagram' in statement_text:
            required_diagram['required_type'] = 'state_machine'
        elif 'flow' in statement_text or 'flowchart' in statement_text:
            required_diagram['required_type'] = 'flowchart'
        elif 'sequence' in statement_text:
            required_diagram['required_type'] = 'sequence'
        elif 'hierarchy' in statement_text or 'hierarchical' in statement_text:
            required_diagram['required_type'] = 'flowchart'  # Hierarchical can be flowchart
        elif 'class' in statement_text:
            required_diagram['required_type'] = 'class'
        elif 'diagram' in statement_text:
            required_diagram['required_type'] = 'diagram_generic'
        
        requirements.append(required_diagram)
    
    return requirements


def check_compliance_satisfaction(requirements: List[Dict[str, Any]], diagrams: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Check if existing diagrams satisfy compliance requirements."""
    satisfied = []
    unsatisfied = []
    
    for requirement in requirements:
        required_type = requirement['required_type']
        found_match = False
        
        for diagram in diagrams:
            # Check if diagram type matches requirement
            if (required_type == 'diagram_generic' or 
                diagram['diagram_type'] == required_type or
                (required_type == 'flowchart' and diagram['diagram_type'] in ['flowchart', 'unknown'])):
                found_match = True
                satisfied.append({
                    'requirement': requirement,
                    'satisfied_by': diagram
                })
                break
        
        if not found_match:
            unsatisfied.append(requirement)
    
    return {
        'satisfied': satisfied,
        'unsatisfied': unsatisfied,
        'satisfaction_rate': len(satisfied) / len(requirements) if requirements else 1.0
    }


def check_file_compliance(file_path: Path) -> Dict[str, Any]:
    """Check diagram compliance for a single ADR file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError) as e:
        return {'error': f"Could not read file: {e}"}
    
    # Find NON-COMPLIANCE statements
    noncompliance_statements = find_noncompliance_statements(content)
    
    # If no NON-COMPLIANCE statements, the file is compliant
    if not noncompliance_statements:
        return {
            'status': 'compliant',
            'has_diagrams': len(find_diagrams(content)) > 0,
            'diagram_count': len(find_diagrams(content))
        }
    
    # Find existing diagrams
    diagrams = find_diagrams(content)
    
    # Analyze requirements
    requirements = analyze_compliance_requirements(noncompliance_statements)
    
    # Check satisfaction
    compliance_check = check_compliance_satisfaction(requirements, diagrams)
    
    if compliance_check['unsatisfied']:
        return {
            'status': 'non_compliant',
            'noncompliance_statements': len(noncompliance_statements),
            'required_diagrams': len(requirements),
            'existing_diagrams': len(diagrams),
            'unsatisfied_requirements': compliance_check['unsatisfied'],
            'satisfaction_rate': compliance_check['satisfaction_rate']
        }
    else:
        return {
            'status': 'compliant_with_diagrams',
            'noncompliance_statements': len(noncompliance_statements),
            'required_diagrams': len(requirements),
            'existing_diagrams': len(diagrams),
            'satisfaction_rate': 1.0
        }


def main():
    """Main execution function."""
    # Base directory for HAIOS project
    base_dir = Path(__file__).parent.parent
    
    # Directory to scan
    adr_dir = base_dir / 'docs' / 'ADR'
    
    if not adr_dir.exists():
        print(f"❌ ADR directory not found: {adr_dir}")
        sys.exit(1)
    
    print("📐 HAIOS ADR Diagram Compliance Checker")
    print("=" * 50)
    
    total_files = 0
    compliant_files = 0
    non_compliant_files = 0
    files_with_noncompliance_statements = 0
    
    # Find all ADR .md files (exclude README and other non-ADR files)
    adr_files = [f for f in adr_dir.glob('ADR-OS-*.md')]
    total_files = len(adr_files)
    
    print(f"📁 Scanning {total_files} ADR files in {adr_dir}")
    print()
    
    for adr_file in adr_files:
        result = check_file_compliance(adr_file)
        
        if result.get('status') == 'error':
            print(f"❌ {adr_file.name}: {result['error']}")
            continue
        
        if result.get('status') == 'compliant':
            compliant_files += 1
            diagram_info = f" ({result['diagram_count']} diagrams)" if result['has_diagrams'] else " (no diagrams)"
            print(f"✅ {adr_file.name}: COMPLIANT{diagram_info}")
        
        elif result.get('status') == 'compliant_with_diagrams':
            compliant_files += 1
            files_with_noncompliance_statements += 1
            print(f"⚠️  {adr_file.name}: COMPLIANT but has NON-COMPLIANCE statements")
            print(f"   ({result['existing_diagrams']} diagrams satisfy {result['required_diagrams']} requirements)")
        
        elif result.get('status') == 'non_compliant':
            non_compliant_files += 1
            files_with_noncompliance_statements += 1
            print(f"🚨 {adr_file.name}: NON-COMPLIANT")
            print(f"   {result['noncompliance_statements']} NON-COMPLIANCE statements")
            print(f"   {result['existing_diagrams']} existing diagrams, {len(result['unsatisfied_requirements'])} requirements unsatisfied")
            
            for unsatisfied in result['unsatisfied_requirements']:
                print(f"   ❌ Missing: {unsatisfied['required_type']} - {unsatisfied['description']}")
    
    print(f"\n📊 SUMMARY")
    print(f"   Total ADR files scanned: {total_files}")
    print(f"   Compliant files: {compliant_files}")
    print(f"   Non-compliant files: {non_compliant_files}")
    print(f"   Files with NON-COMPLIANCE statements: {files_with_noncompliance_statements}")
    
    compliance_rate = (compliant_files / total_files * 100) if total_files > 0 else 100
    print(f"   Overall compliance rate: {compliance_rate:.1f}%")
    
    if non_compliant_files > 0:
        print(f"\n❌ VALIDATION FAILED: {non_compliant_files} files are not diagram compliant")
        sys.exit(1)
    else:
        print(f"\n✅ VALIDATION PASSED: All ADRs are diagram compliant")
        sys.exit(0)


if __name__ == '__main__':
    main()