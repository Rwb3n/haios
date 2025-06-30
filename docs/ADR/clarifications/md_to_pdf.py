import glob
from markdown import Markdown
from xhtml2pdf import pisa

def convert_md_to_pdf():
    # 1. Gather and sort all .md files
    md_files = sorted(glob.glob("*.md"))
    if not md_files:
        print("No Markdown files found.")
        return

    # 2. Build a combined Markdown string with TOC
    combined_md = "[TOC]\n\n"
    for idx, md_path in enumerate(md_files):
        try:
            with open(md_path, encoding='utf-8') as f:
                combined_md += f.read()
        except UnicodeDecodeError:
            with open(md_path, encoding='utf-16') as f:
                combined_md += f.read()
        # Insert a PDF page-break before the next file
        if idx < len(md_files) - 1:
            combined_md += "\n<p style=\"page-break-after: always\"></p>\n"

    # 3. Convert Markdown to HTML (with TOC)
    md = Markdown(extensions=["toc", "fenced_code"])
    html_body = md.convert(combined_md)

    # 4. Wrap in minimal HTML boilerplate
    full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Combined ADRs</title>
</head>
<body>
{html_body}
</body>
</html>"""

    # 5. Render HTML to PDF
    with open("output.pdf", "wb") as pdf_file:
        result = pisa.CreatePDF(full_html, dest=pdf_file)
    if result.err:
        print("❌ Error generating PDF")
        print(result.err)
        print(result.log)
    else:
        print("✅ Successfully created output.pdf")

if __name__ == "__main__":
    convert_md_to_pdf()
