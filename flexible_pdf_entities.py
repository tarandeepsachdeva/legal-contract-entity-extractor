#!/usr/bin/env python3
"""
FLEXIBLE PDF to JSON Pipeline
Processes different PDFs and extracts their unique entities
"""

import sys
import os
import json
import requests
import subprocess
from collections import defaultdict

def extract_text_from_pdf_via_container(pdf_path):
    """Extract text using existing legal-ner-api container"""
    try:
        print(f"📄 Extracting text from: {pdf_path}")
        
        # Get the container ID
        result = subprocess.run(['docker', 'ps', '--filter', 'name=legal-ner-api', '--format', '{{.ID}}'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("❌ legal-ner-api container not running")
            return None
        
        container_id = result.stdout.strip()
        
        # Copy PDF into container
        subprocess.run(['docker', 'cp', pdf_path, f'{container_id}:/tmp/input.pdf'], check=True)
        
        # Extract text inside container
        cmd = [
            'docker', 'exec', container_id,
            'python', '-c',
            '''
import fitz
from pdf2image import convert_from_path
import pytesseract

doc = fitz.open("/tmp/input.pdf")
text = ""

# Try direct text extraction first
for page in doc:
    page_text = page.get_text()
    text += page_text + "\\n"

# If no text found, use OCR
if not text.strip():
    print("Using OCR for scanned PDF...")
    try:
        images = convert_from_path("/tmp/input.pdf", dpi=200)
        for i, image in enumerate(images):
            ocr_text = pytesseract.image_to_string(image)
            text += ocr_text + "\\n"
    except Exception as e:
        print(f"OCR failed: {e}")

print(text)
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            text = result.stdout.strip()
            print(f"✅ Extracted {len(text)} characters")
            print(f"📝 Preview: {text[:200]}...")
            return text
        else:
            print(f"❌ Container extraction failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return None

def extract_entities_via_api(text):
    """Extract entities using running Docker API"""
    try:
        print("🌐 Sending to API...")
        
        response = requests.post('http://localhost:5001/extract', 
                               json={'text': text}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            entity_count = result.get('entity_count', 0)
            entities = result.get('entities', [])
            
            print(f"✅ Extracted {entity_count} entities")
            return result
        else:
            print(f"❌ API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return None

def save_results(result, output_path, pdf_path):
    """Save results to JSON file"""
    if result is None:
        print("❌ No results to save")
        return
    
    entities = result.get('entities', [])
    entity_count = result.get('entity_count', 0)
    
    output = {
        "source_file": pdf_path,
        "total_entities": entity_count,
        "entity_types": list(set(label for _, label in entities)),
        "entities": entities,
        "processing_method": result.get('method', 'api'),
        "processing_time": result.get('processing_time', 0.0),
        "success": result.get('success', False),
        "timestamp": result.get('timestamp', '')
    }
    
    output_file = output_path.replace('.pdf', '_entities.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    print(f"📊 Found {entity_count} entities")
    print(f"🏷️  Entity types: {', '.join(output['entity_types'])}")
    
    print(f"\n📍 ENTITIES FOUND:")
    for entity, label in entities:
        print(f"  {entity} → {label}")

def process_multiple_pdfs(pdf_files):
    """Process multiple PDFs and combine results"""
    all_results = []
    combined_entities = defaultdict(list)
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 Processing PDF {i}/{len(pdf_files)}: {pdf_path}")
        
        # Extract text from PDF
        text = extract_text_from_pdf_via_container(pdf_path)
        if not text:
            print(f"❌ Failed to extract text from {pdf_path}")
            continue
        
        # Extract entities
        result = extract_entities_via_api(text)
        if not result:
            print(f"❌ Failed to extract entities from {pdf_path}")
            continue
        
        entities = result.get('entities', [])
        
        # Add to combined results
        for entity, label in entities:
            combined_entities[label].append(entity)
        
        all_results.append({
            "pdf_file": pdf_path,
            "entities": entities,
            "entity_count": len(entities),
            "entity_types": list(set(label for _, label in entities))
        })
    
    # Create combined output
    output = {
        "total_pdfs": len(pdf_files),
        "combined_entities": dict(combined_entities),
        "total_unique_entities": len(combined_entities),
        "entity_types": list(combined_entities.keys()),
        "processing_method": "hybrid",
        "success": True
    }
    
    combined_file = "combined_results.json"
    with open(combined_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"📊 Total unique entities: {len(output['combined_entities'])}")
    print(f"🏷️  Entity types: {', '.join(output['entity_types'])}")
    
    print(f"\n🎉 COMBINED RESULTS:")
    print(f"📊 Total PDFs processed: {len(pdf_files)}")
    print(f"📊 Total unique entities: {len(output['combined_entities'])}")
    print(f"🏷️  Entity types: {', '.join(output['entity_types'])}")
    print(f"📁 Combined results saved to: {combined_file}")
    
    return all_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python flexible_pdf_entities.py <pdf1> [pdf2] ...")
        print("\nExamples:")
        print("  python flexible_pdf_entities.py pdf1.pdf pdf2.pdf")
        print("  python flexible_pdf_entities.py 'data/raw pdfs/Digital/digital_pdf16.pdf' 'data/raw pdfs/Scanned/scanned_pdf4.pdf'")
        return
    
    pdf_files = sys.argv[1:]
    
    if not pdf_files:
        print("❌ No PDF files provided")
        return
    
    print("🚀 FLEXIBLE PDF to Entity Extraction Pipeline")
    print("=" * 55)
    
    # Check if API is running
    try:
        health_response = requests.get('http://localhost:5001/health', timeout=5)
        if health_response.status_code != 200:
            print("❌ API is not running. Start Docker container first:")
            print("   docker start legal-ner-api")
            return
        print("✅ API is running")
    except:
        print("❌ API is not running. Start Docker container first:")
        print("   docker start legal-ner-api")
        return
    
    # Process all PDFs
    all_results = process_multiple_pdfs(pdf_files)
    
    if all_results:
        print(f"\n🎉 SUCCESS! Processed {len(all_results)} PDFs")
        print(f"📊 Total unique entities across all PDFs: {len(all_results[-1]['combined_entities'])}")
    else:
        print("❌ Failed to process PDFs")

if __name__ == "__main__":
    main()
