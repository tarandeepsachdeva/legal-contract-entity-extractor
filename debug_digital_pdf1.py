#!/usr/bin/env python3
"""
Debug script to see what happened with digital_pdf1
"""

import sys
import os
import json
import requests

# Add the current directory to the path to import from clean_pdf_entities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_pdf_entities import extract_text_from_pdf_via_container, extract_entities_via_api

def debug_digital_pdf1():
    """Debug the digital_pdf1 processing"""
    
    pdf_path = "data/raw pdfs/Digital/digital_pdf1.pdf"
    
    print("🔍 DEBUGGING DIGITAL PDF 1")
    print("=" * 50)
    
    # Step 1: Check if API is running
    try:
        health_response = requests.get('http://localhost:5001/health', timeout=5)
        if health_response.status_code != 200:
            print("❌ API is not running")
            return
        print("✅ API is running")
    except:
        print("❌ API is not running")
        return
    
    # Step 2: Extract text
    print(f"\n📄 Extracting text from: {pdf_path}")
    text = extract_text_from_pdf_via_container(pdf_path)
    
    if not text:
        print("❌ Failed to extract text")
        return
    
    print(f"✅ Extracted {len(text)} characters")
    print(f"📝 First 500 characters: {text[:500]}...")
    
    # Step 3: Try API call with debugging
    print(f"\n🌐 Sending to API...")
    try:
        response = requests.post('http://localhost:5001/extract', 
                               json={'text': text}, timeout=30)
        
        print(f"📊 Response status code: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API returned {len(result.get('entities', []))} entities")
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"📝 Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")

if __name__ == "__main__":
    debug_digital_pdf1()
