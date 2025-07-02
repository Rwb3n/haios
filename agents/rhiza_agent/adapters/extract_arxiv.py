import sys
import json
import httpx
import fitz  # PyMuPDF

def extract_arxiv_pdf_data(paper_id: str):
    """
    Downloads an arXiv paper PDF, extracts its text and metadata.
    """
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    # The abstract page is still useful for easily grabbing bibliographic metadata.
    abs_url = f"https://arxiv.org/abs/{paper_id}"
    
    try:
        # --- Step 1: Download the PDF content ---
        with httpx.stream("GET", pdf_url, follow_redirects=True, timeout=30.0) as r:
            r.raise_for_status()
            pdf_bytes = r.read()

        # --- Step 2: Extract text from the PDF ---
        # This is our primary, stable source of the paper's content.
        raw_text_content = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                raw_text_content += page.get_text()

        # --- Step 3: Scrape the abstract page for stable metadata ---
        # While the HTML can change, these meta tags are highly stable as they are used by search engines.
        # This is more robust than scraping visible HTML elements.
        from bs4 import BeautifulSoup
        
        meta_response = httpx.get(abs_url, timeout=20.0)
        meta_response.raise_for_status()
        soup = BeautifulSoup(meta_response.text, 'html.parser')
        
        title = soup.find("meta", property="og:title")['content']
        authors = [meta['content'] for meta in soup.find_all("meta", attrs={"name": "citation_author"})]
        abstract = soup.find("meta", property="og:description")['content']
        
        # --- Step 4: Structure the final output ---
        structured_data = {
            "paper_id": paper_id,
            "source_pdf_url": pdf_url,
            "source_abs_url": abs_url,
            "metadata": {
                "title": title,
                "authors": authors,
                "abstract": abstract
            },
            # The raw text is the core "evidence" from the stable source.
            "raw_text_from_pdf": raw_text_content,
        }
        
        print(json.dumps(structured_data, indent=2))

    except Exception as e:
        print(f"Error processing paper {paper_id}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_arxiv_pdf.py <paper_id>", file=sys.stderr)
        sys.exit(1)
    
    paper_id_arg = sys.argv[1]
    extract_arxiv_pdf_data(paper_id_arg)