#!/usr/bin/env python3
"""
Debug script to see what date-related entities are being extracted
"""

import sys
import os
import json
import requests

# Add the current directory to the path to import from clean_pdf_entities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_pdf_entities import extract_text_from_pdf_via_container, extract_entities_via_api

def debug_date_entities(pdf_path):
    """Debug date entity extraction"""
    
    print(f"🔍 DEBUGGING DATE ENTITIES FOR: {pdf_path}")
    print("=" * 60)
    
    # Step 1: Extract text
    print(f"\n📄 Extracting text...")
    text = extract_text_from_pdf_via_container(pdf_path)
    
    if not text:
        print("❌ Failed to extract text")
        return
    
    print(f"✅ Extracted {len(text)} characters")
    
    # Step 2: Look for date patterns in text
    print(f"\n🔍 Searching for date patterns in text...")
    
    import re
    
    # Common date patterns
    date_patterns = [
        r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b',  # 12/31/2008, 12-31-2008
        r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',  # January 31, 2008
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # January 31, 2008
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',  # Jan 31, 2008
        r'\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',  # 31 Jan 2008
        r'\bexpiration\b.*?\d{1,4}[^.]*',  # expiration followed by numbers
        r'\bexpire\b.*?\d{1,4}[^.]*',  # expire followed by numbers
        r'\bterm\b.*?\d{1,4}[^.]*',  # term followed by numbers
        r'\bvalid\b.*?\d{1,4}[^.]*',  # valid followed by numbers
        r'\buntil\b.*?\d{1,4}[^.]*',  # until followed by numbers
        r'\bthrough\b.*?\d{1,4}[^.]*',  # through followed by numbers
    ]
    
    found_dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                date_str = ' '.join(match)
            else:
                date_str = match
            
            # Get some context around the date
            date_index = text.lower().find(date_str.lower())
            if date_index != -1:
                start = max(0, date_index - 50)
                end = min(len(text), date_index + len(date_str) + 50)
                context = text[start:end].replace('\n', ' ').strip()
                found_dates.append((date_str, context))
    
    print(f"📅 Found {len(found_dates)} date patterns:")
    for i, (date, context) in enumerate(found_dates[:10]):  # Show first 10
        print(f"  {i+1}. '{date}'")
        print(f"     Context: ...{context}...")
    
    # Step 3: Get API entities
    print(f"\n🌐 Getting entities from API...")
    result = extract_entities_via_api(text)
    
    if result:
        entities = result.get('entities', [])
        print(f"✅ API returned {len(entities)} total entities")
        
        # Filter for date-related entities
        date_entities = []
        for entity_text, entity_type in entities:
            if any(word in entity_text.lower() for word in ['date', 'expiration', 'expire', 'term', 'valid', 'until', 'through', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
                date_entities.append((entity_text, entity_type))
        
        print(f"📅 Date-related entities from API:")
        for i, (entity, entity_type) in enumerate(date_entities):
            print(f"  {i+1}. '{entity}' → {entity_type}")
        
        # Show all entity types found
        entity_types = set(label for _, label in entities)
        print(f"\n🏷️  All entity types found: {', '.join(sorted(entity_types))}")
    
    else:
        print("❌ Failed to get entities from API")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        debug_date_entities(sys.argv[1])
    else:
        print("Usage: python debug_dates.py <pdf_file>")
        print("Example: python debug_dates.py 'data/raw pdfs/Digital/digital_pdf2.pdf'")
