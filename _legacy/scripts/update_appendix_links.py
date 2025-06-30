"""update_appendix_links.py
Batch link-updater to migrate old doc paths to new Appendix locations.
Run from project root:  
    python scripts/update_appendix_links.py
The script walks all *.md files under docs/ and replaces legacy paths
with their corresponding Appendix paths, emitting a summary of changes.
"""
from pathlib import Path
import re

# Mapping of legacy relative path substrings -> new appendix path
PATH_MAP = {
    "docs/Document_1/I-OVERALL_MANDATE_CORE_PRINCIPLES.md": "docs/appendices/Appendix_A_Assumptions_Constraints.md",
    "docs/Document_1/II-DATA_ECOSYSTEM_OVERVIEW.md": "docs/appendices/Appendix_A_Assumptions_Constraints.md",
    "docs/Document_1/III-D-ARTIFACT_LIFECYCLE_ANNOTATIONS.md": "docs/appendices/Appendix_A_Assumptions_Constraints.md",
    "docs/Document_1/III-E-REPORTING_REVIEWS.md": "docs/appendices/Appendix_A_Assumptions_Constraints.md",
    "docs/Document_1/IV-PHASE_INTENTS_CORE_AI_ACTIONS.md": "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/Document_1/V-CONTINUITY_ERROR_HANDLING_STATE_MANAGEMENT.md": "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/Document_1/VI-FINAL-MANDATE.md": "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/Document_1/core_operations_phase_lock.md": "docs/appendices/Appendix_B_Operational_Principles_Roles_Error_Handling.md",
    "docs/Document_3/Scaffold Definition Specification.md": "docs/appendices/Appendix_C_Scaffold_Definition_Template.md",
    "docs/guidelines/test_guidelines.md": "docs/appendices/Appendix_F_Testing_Guidelines.md",
    "docs/source/frameworks_registry.md": "docs/appendices/Appendix_G_Frameworks_Registry.md",
    "docs/CI_CD_SETUP.md": "docs/appendices/Appendix_H_CI_CD_Policy_Pipeline_Reference.md",
}

MD_ROOT = Path("docs")
CHANGED = []

for md_file in MD_ROOT.rglob("*.md"):
    try:
        text = md_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Skip non-utf8 markdown files (rare)
        continue
    original = text
    for old, new in PATH_MAP.items():
        # Replace both markdown link formats and plain path mentions
        text = re.sub(re.escape(old), new, text)
    if text != original:
        md_file.write_text(text, encoding="utf-8")
        CHANGED.append(md_file.as_posix())

print(f"Updated links in {len(CHANGED)} file(s).")
for f in CHANGED:
    print(f" - {f}") 