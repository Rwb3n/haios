import sys
import json
import httpx
import xml.etree.ElementTree as ET

# NocoDB/SQLite would be accessed via its REST API.
# These would be configured via environment variables for security.
NOCODB_API_URL = "http://nocodb:8080/api/v1/db/data/noco/p_.../views/v_..." # Example
NOCODB_API_TOKEN = "YOUR_XC_TOKEN"

def get_existing_ids_from_db():
    """Queries the NocoDB API to get all paper_ids already ingested."""
    headers = {"xc-token": NOCODB_API_TOKEN}
    try:
        # Assuming an API endpoint that can return all paper_ids
        response = httpx.get(f"{NOCODB_API_URL}?fields=paper_id", headers=headers, timeout=20.0)
        response.raise_for_status()
        records = response.json().get("list", [])
        return {item.get("paper_id") for item in records}
    except Exception as e:
        print(f"Error fetching existing IDs from database: {e}", file=sys.stderr)
        return set()

def poll_arxiv_for_new(category: str):
    """Polls arXiv Atom feed and returns IDs not present in the database."""
    arxiv_api_url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results=50"
    
    try:
        existing_ids = get_existing_ids_from_db()
        
        response = httpx.get(arxiv_api_url, timeout=20.0)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        new_paper_ids = []
        for entry in root.findall('atom:entry', namespace):
            # ArXiv API URL is like http://arxiv.org/abs/2401.12345v1, we want the core ID
            full_id = entry.find('atom:id', namespace).text
            paper_id = full_id.split('/abs/')[-1].split('v')[0]
            
            if paper_id not in existing_ids:
                new_paper_ids.append(paper_id)
        
        # Output is a simple JSON list of strings
        print(json.dumps(new_paper_ids))

    except Exception as e:
        print(f"Error polling arXiv for category {category}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python poll_arxiv_new.py <category>", file=sys.stderr)
        sys.exit(1)
    
    category_arg = sys.argv[1]
    poll_arxiv_for_new(category_arg)