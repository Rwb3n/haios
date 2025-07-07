#!/usr/bin/env python3
"""
Cross-Reference Link Validator for HAIOS ADR Canon

This script finds all internal links (ADR references, relative file paths) 
within the docs/ tree and verifies that target files exist.

Part of: EXEC_PLAN_AUTOMATE_ADR_HYGIENE_V1  
Addresses: ADR drift risk from broken internal references
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from urllib.parse import urlparse


def extract_internal_links(content: str, source_file: Path) -> List[Dict[str, Any]]:
    """Extract internal links from markdown content."""
    links = []
    
    # Pattern 1: ADR references [ADR-OS-XXX](relative/path)
    adr_pattern = r'\[ADR-OS-(\d+)\]\(([^)]+)\)'
    adr_matches = re.finditer(adr_pattern, content)
    
    for match in adr_matches:
        adr_num = match.group(1)
        link_path = match.group(2)
        links.append({
            'type': 'adr_reference',
            'text': match.group(0),
            'adr_number': adr_num,
            'target_path': link_path,
            'line_context': content[max(0, match.start()-50):match.end()+50]
        })
    
    # Pattern 2: Relative file paths [text](./path/to/file) or [text](../path/to/file)
    relative_pattern = r'\[([^\]]+)\]\((\./[^)]+|\.\./[^)]+)\)'
    relative_matches = re.finditer(relative_pattern, content)
    
    for match in relative_matches:
        link_text = match.group(1)
        link_path = match.group(2)
        links.append({
            'type': 'relative_path',
            'text': match.group(0),
            'link_text': link_text,
            'target_path': link_path,
            'line_context': content[max(0, match.start()-50):match.end()+50]
        })
    
    # Pattern 3: Absolute internal paths [text](/docs/path/to/file)
    absolute_pattern = r'\[([^\]]+)\]\((/docs/[^)]+)\)'
    absolute_matches = re.finditer(absolute_pattern, content)
    
    for match in absolute_matches:
        link_text = match.group(1)
        link_path = match.group(2)
        links.append({
            'type': 'absolute_path',
            'text': match.group(0),
            'link_text': link_text,
            'target_path': link_path,
            'line_context': content[max(0, match.start()-50):match.end()+50]
        })
    
    # Pattern 4: Appendix references [Appendix X](path)
    appendix_pattern = r'\[Appendix[ _]([A-Z])[^\]]*\]\(([^)]+)\)'
    appendix_matches = re.finditer(appendix_pattern, content)
    
    for match in appendix_matches:
        appendix_letter = match.group(1)
        link_path = match.group(2)
        links.append({
            'type': 'appendix_reference',
            'text': match.group(0),
            'appendix_letter': appendix_letter,
            'target_path': link_path,
            'line_context': content[max(0, match.start()-50):match.end()+50]
        })
    
    return links


def resolve_link_path(link: Dict[str, Any], source_file: Path, base_dir: Path) -> Path:
    """Resolve a link path to an absolute file path."""
    target_path = link['target_path']
    
    # Remove fragments and query parameters
    if '#' in target_path:
        target_path = target_path.split('#')[0]
    if '?' in target_path:
        target_path = target_path.split('?')[0]
    
    # Skip empty paths
    if not target_path:
        return None
    
    # Handle different path types
    if target_path.startswith('./'):
        # Relative to current directory
        resolved = source_file.parent / target_path[2:]
    elif target_path.startswith('../'):
        # Relative to parent directory
        resolved = source_file.parent / target_path
    elif target_path.startswith('/docs/'):
        # Absolute path from project root
        resolved = base_dir / target_path[1:]  # Remove leading slash
    else:
        # Assume relative to current directory
        resolved = source_file.parent / target_path
    
    return resolved.resolve()


def validate_links(file_path: Path, base_dir: Path) -> Dict[str, Any]:
    """Validate all internal links in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, IOError) as e:
        return {'error': f"Could not read file: {e}"}
    
    links = extract_internal_links(content, file_path)
    
    if not links:
        return {'status': 'no_links', 'total_links': 0}
    
    broken_links = []
    valid_links = []
    
    for link in links:
        resolved_path = resolve_link_path(link, file_path, base_dir)
        
        if resolved_path is None:
            broken_links.append({
                **link,
                'error': 'Empty target path'
            })
            continue
        
        if resolved_path.exists():
            valid_links.append({
                **link,
                'resolved_path': str(resolved_path)
            })
        else:
            broken_links.append({
                **link,
                'resolved_path': str(resolved_path),
                'error': 'Target file does not exist'
            })
    
    result = {
        'status': 'broken_links' if broken_links else 'all_valid',
        'total_links': len(links),
        'valid_links': len(valid_links),
        'broken_links': len(broken_links)
    }
    
    if broken_links:
        result['broken_link_details'] = broken_links
    
    return result


def main():
    """Main execution function."""
    # Base directory for HAIOS project
    base_dir = Path(__file__).parent.parent
    
    # Directory to scan
    docs_dir = base_dir / 'docs'
    
    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        sys.exit(1)
    
    print("🔗 HAIOS ADR Cross-Reference Link Validator")
    print("=" * 50)
    
    total_files = 0
    files_with_links = 0
    files_with_broken_links = 0
    total_links = 0
    total_broken_links = 0
    
    # Find all .md files in docs/ recursively
    md_files = list(docs_dir.glob('**/*.md'))
    total_files = len(md_files)
    
    print(f"📁 Scanning {total_files} markdown files in {docs_dir}")
    print()
    
    for md_file in md_files:
        result = validate_links(md_file, base_dir)
        
        if result.get('status') == 'error':
            print(f"❌ {md_file.relative_to(base_dir)}: {result['error']}")
            continue
        
        if result.get('status') == 'no_links':
            print(f"⚪ {md_file.relative_to(base_dir)}: No internal links found")
            continue
        
        files_with_links += 1
        total_links += result.get('total_links', 0)
        
        if result.get('status') == 'broken_links':
            files_with_broken_links += 1
            total_broken_links += result['broken_links']
            
            print(f"🚨 {md_file.relative_to(base_dir)}: {result['broken_links']}/{result['total_links']} BROKEN LINKS")
            
            for broken_link in result['broken_link_details']:
                print(f"   ❌ {broken_link['type']}: {broken_link['text']}")
                print(f"      Target: {broken_link['target_path']}")
                print(f"      Resolved: {broken_link.get('resolved_path', 'N/A')}")
                print(f"      Error: {broken_link['error']}")
                print(f"      Context: ...{broken_link['line_context']}...")
                print()
        
        elif result.get('status') == 'all_valid':
            print(f"✅ {md_file.relative_to(base_dir)}: All {result['total_links']} links valid")
    
    print(f"\n📊 SUMMARY")
    print(f"   Total files scanned: {total_files}")
    print(f"   Files with internal links: {files_with_links}")
    print(f"   Files with broken links: {files_with_broken_links}")
    print(f"   Total internal links: {total_links}")
    print(f"   Total broken links: {total_broken_links}")
    
    if files_with_broken_links > 0:
        print(f"\n❌ VALIDATION FAILED: {files_with_broken_links} files have broken internal links")
        sys.exit(1)
    else:
        print(f"\n✅ VALIDATION PASSED: All internal links are valid")
        sys.exit(0)


if __name__ == '__main__':
    main()