"""Downloads PDFs from arXiv links and saves them locally.
    
    Args:
        papers (list): List of dictionaries with 'title' and 'url' keys
        save_dir (str): Target directory for PDF storage (default: current dir)
    """

import requests
import os
from pathvalidate import sanitize_filename  # Optional for safer filenames

def download_arxiv_pdfs(papers, save_dir="."):

    os.makedirs(save_dir, exist_ok=True)
    
    for paper in papers:
        title = paper['title']
        pdf_url = f"{paper['url']}.pdf"  # Ensure .pdf extension
        filename = sanitize_filename(title[:150]) + ".pdf"  # Truncate long titles
        
        try:
            response = requests.get(pdf_url, allow_redirects=True)
            response.raise_for_status()
            
            full_path = os.path.join(save_dir, filename)
            with open(full_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Success: {filename}")
        except Exception as e:
            print(f"❌ Failed: {title} - {str(e)}")

#download_arxiv_pdfs(papers)
