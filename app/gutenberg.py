import requests
import re
from fastapi import HTTPException

def fetch_gutenberg_text(book_id: int) -> str:
    """
    Download book text from Project Gutenberg.
    Tries multiple URL formats to find the book.
    """
    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200 and len(response.text) > 1000:
                return response.text
        except requests.RequestException:
            continue
    
    raise HTTPException(
        status_code=404, 
        detail=f"Book {book_id} not found on Project Gutenberg"
    )

def strip_headers(text: str) -> str:
    """
    Remove Project Gutenberg header and footer boilerplate.
    These sections contain legal text and aren't part of the actual book.
    """
    # Find start marker
    start_patterns = [
        r"\*\*\* START OF THIS PROJECT GUTENBERG",
        r"\*\*\* START OF THE PROJECT GUTENBERG",
    ]
    
    # Find end marker
    end_patterns = [
        r"\*\*\* END OF THIS PROJECT GUTENBERG",
        r"\*\*\* END OF THE PROJECT GUTENBERG",
    ]
    
    start_match = None
    for pattern in start_patterns:
        start_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if start_match:
            break
    
    end_match = None
    for pattern in end_patterns:
        end_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if end_match:
            break
    
    if start_match and end_match:
        return text[start_match.end():end_match.start()].strip()
    
    return text.strip()