#!/usr/bin/env python3
"""
Debug script to see what happened with scanned_pdf1
"""

import sys
import os
import json
import requests
import subprocess

# Add the current directory to the path to import from clean_pdf_entities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_pdf_entities import extract_text_from_pdf_via_container, extract_entities_via_api, clean_entities, validate_entity_quality, reclassify_misidentified_entities

def debug_scanned_pdf1():
    """Debug the scanned_pdf1 processing"""
    
    pdf_path = "data/raw pdfs/Scanned/scanned_pdf1.pdf"
    
    print("🔍 DEBUGGING SCANNED PDF 1")
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
    
    # Step 3: Get raw entities from API
    print(f"\n🌐 Getting raw entities from API...")
    result = extract_entities_via_api(text)
    
    if not result:
        print("❌ Failed to get entities from API")
        return
    
    raw_entities = result.get('entities', [])
    print(f"✅ API returned {len(raw_entities)} raw entities")
    
    if raw_entities:
        print(f"\n📍 RAW ENTITIES FROM API:")
        for i, (entity, label) in enumerate(raw_entities):
            print(f"  {i+1}. '{entity}' → {label}")
    else:
        print("  No entities returned by API")
        return
    
    # Step 4: Apply cleaning step by step
    print(f"\n🧹 APPLYING CLEANING STEP BY STEP...")
    
    # Basic cleaning
    cleaned_entities = clean_entities(raw_entities)
    print(f"After basic cleaning: {len(cleaned_entities)} entities")
    
    if len(cleaned_entities) != len(raw_entities):
        print("  Entities removed in basic cleaning:")
        for i, (entity, label) in enumerate(raw_entities):
            if (entity, label) not in cleaned_entities:
                print(f"    REMOVED: '{entity}' → {label}")
    
    # Reclassification
    reclassified_entities = reclassify_misidentified_entities(cleaned_entities)
    print(f"After reclassification: {len(reclassified_entities)} entities")
    
    if len(reclassified_entities) != len(cleaned_entities):
        print("  Reclassifications made:")
        for (clean_text, clean_type), (reclass_text, reclass_type) in zip(cleaned_entities, reclassified_entities):
            if clean_type != reclass_type:
                print(f"    '{clean_text}': {clean_type} → {reclass_type}")
    
    # Validation
    validated_entities = []
    for entity_text, entity_type in reclassified_entities:
        if validate_entity_quality(entity_text, entity_type):
            validated_entities.append((entity_text, entity_type))
        else:
            print(f"    VALIDATION FAILED: '{entity_text}' → {entity_type}")
    
    print(f"After validation: {len(validated_entities)} entities")
    
    # Final result
    if validated_entities:
        print(f"\n✅ FINAL VALID ENTITIES:")
        for entity, label in validated_entities:
            print(f"  '{entity}' → {label}")
    else:
        print(f"\n❌ NO VALID ENTITIES REMAIN")

if __name__ == "__main__":
    debug_scanned_pdf1()
