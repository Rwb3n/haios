import pathlib
import sys
from typing import List

TEMPLATE_HEADER = "## Initial Clarification Draft (TBD)\n"
RESPONSES_BLOCK = (
    "## Responses\n"
    "| # | Response By | Date | Related Q# | Summary |\n"
    "|---|-------------|------|------------|---------|\n"
    "| 1 | _placeholder_ | | | |\n\n"
    "## Formal Reviews & Dissents\n"
    "<!-- Capture formal approvals, objections, and alternative viewpoints here. -->\n"
)

def process_file(fp: pathlib.Path) -> bool:
    text = fp.read_text(encoding="utf-8").splitlines(True)
    changed = False

    # 1. Ensure Initial Clarification Draft header exists after title line
    if len(text) > 1 and "Initial Clarification Draft" not in "".join(text[:5]):
        text.insert(1, "\n" + TEMPLATE_HEADER + "\n")
        changed = True

    # 2. Replace placeholder Responses section
    content = "".join(text)
    if "## Responses\n<!--" in content:
        content = content.replace(
            "## Responses\n<!-- Threaded responses or resolutions; update 'Status' in table above -->",
            RESPONSES_BLOCK,
        )
        changed = True
    text = content.splitlines(True)

    # 3. Append Formal Reviews section if missing
    if "## Formal Reviews & Dissents" not in content:
        # Find Distributed checklist section end
        idx = next((i for i,l in enumerate(text) if l.startswith("## Distributed-Systems Protocol Compliance Checklist")), None)
        if idx is not None:
            # find following blank line after checklist bullets
            end_idx = idx
            while end_idx < len(text) and text[end_idx].strip():
                end_idx += 1
            text.insert(end_idx + 1, "\n" + RESPONSES_BLOCK.split("\n",1)[1])
            changed = True
    if changed:
        fp.write_text("".join(text), encoding="utf-8")
    return changed


def main(files: List[str]):
    if not files:
        base_dir = pathlib.Path("docs/ADR/clarifications")
        files = [str(p) for p in base_dir.glob("ADR-OS-*_clarification.md") if p.is_file()]
    updated = 0
    for f in files:
        if process_file(pathlib.Path(f)):
            updated += 1
    print(f"Updated {updated} clarification files.")

if __name__ == "__main__":
    main(sys.argv[1:]) 