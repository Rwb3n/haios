#!/usr/bin/env python3
"""
Annotation Duplicate Detector for HAIOS ADR Canon

This script scans all .md files in docs/ADR/ and docs/appendices/ for 
EmbeddedAnnotationBlocks and flags any files with duplicate entries in 
source_documents or other key fields.

Part of: EXEC_PLAN_AUTOMATE_ADR_HYGIENE_V1
Addresses: ADR drift risk from manual editing errors
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


def find_annotation_blocks(content: str) -> List[Dict[str, Any]]:
    """Extract EmbeddedAnnotationBlocks from markdown content."""
    blocks = []
    
    # Pattern to match annotation blocks
    pattern = r'```json\s*\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        try:
            parsed = json.loads(match)
            # Check if this looks like an annotation block
            if isinstance(parsed, dict) and any(key in parsed for key in 
                ['source_documents', 'external_references', 'related_adrs', 'frameworks_compliance']):
                blocks.append(parsed)
        except json.JSONDecodeError:
            # Skip malformed JSON
            continue
    
    return blocks


def check_for_duplicates(annotation_block: Dict[str, Any]) -> Dict[str, List[str]]:
    """Check for duplicate values in annotation block arrays."""
    duplicates = {}
    
    # Fields to check for duplicates
    array_fields = ['source_documents', 'external_references', 'related_adrs', 'frameworks_compliance']
    
    for field in array_fields:
        if field in annotation_block:
            value = annotation_block[field]
            if isinstance(value, list):
                seen = set()
                dupes = []
                for item in value:
                    if item in seen:
                        dupes.append(item)
                    else:
                        seen.add(item)
                
                if dupes:
                    duplicates[field] = dupes
    
    return duplicates


def scan_file(file_path: Path) -> Dict[str, Any]:
    """Scan a single file for annotation duplicate issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError) as e:
        return {'error': f"Could not read file: {e}"}
    
    annotation_blocks = find_annotation_blocks(content)
    
    if not annotation_blocks:
        return {'status': 'no_annotations'}
    
    issues = []
    for i, block in enumerate(annotation_blocks):
        duplicates = check_for_duplicates(block)
        if duplicates:
            issues.append({
                'block_index': i,
                'duplicates': duplicates
            })
    
    if issues:
        return {
            'status': 'duplicates_found',
            'total_blocks': len(annotation_blocks),
            'issues': issues
        }
    else:
        return {
            'status': 'clean',
            'total_blocks': len(annotation_blocks)
        }


def main():
    """Main execution function."""
    # Base directory for HAIOS project
    base_dir = Path(__file__).parent.parent
    
    # Directories to scan
    scan_dirs = [
        base_dir / 'docs' / 'ADR',
        base_dir / 'docs' / 'appendices'
    ]
    
    total_files = 0
    files_with_issues = 0
    files_with_annotations = 0
    
    print("🔍 HAIOS ADR Annotation Duplicate Detector")
    print("=" * 50)
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            print(f"⚠️  Directory not found: {scan_dir}")
            continue
        
        print(f"\n📁 Scanning: {scan_dir}")
        
        # Find all .md files
        md_files = list(scan_dir.glob('*.md'))
        total_files += len(md_files)
        
        for md_file in md_files:
            result = scan_file(md_file)
            
            if result.get('status') == 'error':
                print(f"❌ {md_file.name}: {result['error']}")
                continue
            
            if result.get('status') == 'no_annotations':
                print(f"⚪ {md_file.name}: No annotation blocks found")
                continue
            
            files_with_annotations += 1
            
            if result.get('status') == 'duplicates_found':
                files_with_issues += 1
                print(f"🚨 {md_file.name}: DUPLICATES FOUND")
                
                for issue in result['issues']:
                    print(f"   Block {issue['block_index'] + 1}:")
                    for field, dupes in issue['duplicates'].items():
                        print(f"     - {field}: {dupes}")
                
            elif result.get('status') == 'clean':
                print(f"✅ {md_file.name}: Clean ({result['total_blocks']} blocks)")
    
    print(f"\n📊 SUMMARY")
    print(f"   Total files scanned: {total_files}")
    print(f"   Files with annotations: {files_with_annotations}")
    print(f"   Files with duplicate issues: {files_with_issues}")
    
    if files_with_issues > 0:
        print(f"\n❌ VALIDATION FAILED: {files_with_issues} files have duplicate annotations")
        sys.exit(1)
    else:
        print(f"\n✅ VALIDATION PASSED: No duplicate annotations found")
        sys.exit(0)


if __name__ == '__main__':
    main()