#!/usr/bin/env python3
"""
Check the actual text content for expiration dates
"""

import sys
import os

# Add the current directory to the path to import from clean_pdf_entities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_pdf_entities import extract_text_from_pdf_via_container

def check_text_for_expirations(pdf_path):
    """Check text content for expiration-related terms"""
    
    print(f"🔍 CHECKING TEXT CONTENT FOR EXPIRATIONS: {pdf_path}")
    print("=" * 70)
    
    # Extract text
    text = extract_text_from_pdf_via_container(pdf_path)
    
    if not text:
        print("❌ Failed to extract text")
        return
    
    print(f"✅ Extracted {len(text)} characters")
    
    # Look for expiration-related terms in context
    import re
    
    # Find all lines containing expiration keywords
    expiration_keywords = ['expir', 'terminat', 'valid until', 'valid thru', 'expires', 'expiry']
    
    lines = text.split('\n')
    expiration_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in expiration_keywords):
            # Get some context around this line
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context = '\n'.join(lines[start:end])
            expiration_lines.append((i + 1, line.strip(), context))
    
    print(f"\n📅 Found {len(expiration_lines)} lines with expiration-related terms:")
    for line_num, line, context in expiration_lines:
        print(f"\n  Line {line_num}: {line}")
        print(f"  Context:\n{context}")
        print("-" * 50)
    
    # Also search for common date patterns that might be expiration dates
    print(f"\n🔍 Searching for date patterns near expiration terms...")
    
    # Look for dates within 50 characters of expiration keywords
    for keyword in expiration_keywords:
        pattern = f'.{{0,50}}{keyword}.{{0,50}}'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            context_text = match.group()
            print(f"\n  Found '{keyword}' in context:")
            print(f"  {context_text}")
            
            # Look for dates in this context
            date_patterns = [
                r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b',
                r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',
            ]
            
            for date_pattern in date_patterns:
                date_matches = re.findall(date_pattern, context_text, re.IGNORECASE)
                if date_matches:
                    print(f"  📅 Potential dates found: {date_matches}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_text_for_expirations(sys.argv[1])
    else:
        print("Usage: python check_text_content.py <pdf_file>")
        print("Checking: data/raw pdfs/Digital/digital_pdf3.pdf")
