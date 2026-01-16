#!/usr/bin/env python3
"""
ULTIMATE CLEAN PDF to JSON Pipeline
No caching, direct API calls, fresh results
"""

import sys
import os
import json
import requests
import subprocess
import re
from typing import List, Tuple

def clean_entities(entities: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Clean and deduplicate entities extracted from NER model
    """
    if not entities:
        return []
    
    cleaned_entities = []
    seen_entities = set()
    
    # Common words/phrases that should not be entities
    blacklist = {
        'to', 'of', 'and', 'in', 'with', 'as', 'by', 'for', 'on', 'at', 'from',
        'the', 'a', 'an', 'or', 'but', 'not', 'be', 'is', 'are', 'was', 'were',
        'that', 'this', 'these', 'those', 'it', 'they', 'them', 'their', 'its',
        'certain', 'add', 'secure', 'support', 'facilitate', 'production', 'health',
        'necessary', 'assistance', 'testing', 'evaluation', 'acquisition', 'drugs',
        'excipients', 'components', 'activities', 'development', 'agreement',
        'both', 'parties'
    }
    
    for entity_text, entity_type in entities:
        # Skip if entity is too short or empty
        if not entity_text or len(entity_text.strip()) < 3:
            continue
        
        # Clean the entity text
        cleaned_text = entity_text.strip()
        
        # Remove extra whitespace and normalize
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Remove newlines and clean up spacing around them
        cleaned_text = re.sub(r'\s*\n\s*', ' ', cleaned_text)
        
        # Skip if entity is just a common word or phrase
        words = cleaned_text.lower().split()
        if len(words) == 1 and words[0] in blacklist:
            continue
        
        # Skip if entity starts with common stop words (likely sentence fragments)
        if words and words[0] in {'to', 'of', 'and', 'in', 'with', 'as', 'by', 'for'}:
            continue
        
        # Skip entities that are too generic for certain types
        if entity_type == 'PARTY' and len(words) <= 2:
            if any(word in blacklist for word in words):
                continue
        
        if entity_type == 'LOCATION' and len(words) <= 3:
            if any(word in blacklist for word in words):
                continue
        
        # Create a normalized key for deduplication
        normalized_key = (cleaned_text.lower(), entity_type)
        
        # Skip duplicates
        if normalized_key in seen_entities:
            continue
        
        seen_entities.add(normalized_key)
        cleaned_entities.append((cleaned_text, entity_type))
    
    return cleaned_entities

def validate_entity_quality(entity_text: str, entity_type: str) -> bool:
    """
    Additional validation for entity quality based on type
    """
    text = entity_text.strip()
    
    # Basic length checks
    if len(text) < 3 or len(text) > 200:
        return False
    
    # Type-specific validation
    if entity_type == 'EFFECTIVE_DATE':
        # Should contain date-like patterns (be more lenient with OCR)
        date_patterns = [
            r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',
            r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?',  # More lenient for OCR
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns)
    
    elif entity_type == 'PARTY':
        # Should contain company names or person names
        # Be more lenient with company names
        if len(text.split()) < 1:
            return False
        
        # Allow company indicators
        company_indicators = ['LLC', 'Inc', 'Corp', 'Ltd', 'Company', 'Corporation', 'Funding', 'Finance', 'Commercial', 'Acquisition', 'Recovery', 'Solutions']
        if any(indicator in text for indicator in company_indicators):
            return True
            
        # Skip if it looks like a sentence fragment (but be more lenient)
        stop_words = {'to', 'of', 'and', 'in', 'with', 'as', 'by', 'for'}
        words = text.lower().split()
        if words and words[0] in stop_words and len(words) <= 3:
            return False
    
    elif entity_type == 'LOCATION':
        # Should contain location-like information
        # Skip generic descriptions
        generic_words = ['assistance', 'testing', 'evaluation', 'acquisition', 'development', 'terms', 'conditions', 'covenants', 'rights', 'duties', 'obligations', 'guaranties', 'assurances', 'promises']
        if any(word in text.lower() for word in generic_words):
            return False
        
        # Check if this looks like a person name or company - if so, it's probably misclassified
        person_patterns = [
            r',\s*(President|Vice|CEO|Director|Manager|Attorney|Counsel)',
            r'\b(Ltd|Inc|Corp|LLC|Company|Laboratories|Pharma|Funding|Finance|Commercial|Acquisition|Recovery|Solutions)\b',
            r'^[A-Z][a-z]+,\s+[A-Z][a-z]+',
            r'\b(Manager|By)\s+[A-Z]'
        ]
        
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in person_patterns):
            return False  # This is likely a person/company, not a location
        
        # Allow actual locations
        location_indicators = ['NY', 'NJ', 'USA', 'New York', 'California', 'Texas', 'Florida']
        if any(indicator in text for indicator in location_indicators):
            return True
    
    elif entity_type == 'AGREEMENT_TYPE':
        # Should contain agreement-related terms
        agreement_keywords = ['agreement', 'contract', 'terms', 'conditions', 'protocol', 'memorandum', 'letter', 'commitment', 'loan', 'security']
        if not any(keyword in text.lower() for keyword in agreement_keywords):
            return False
    
    return True

def reclassify_misidentified_entities(entities: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Reclassify entities that are clearly misidentified
    """
    reclassified = []
    
    for entity_text, entity_type in entities:
        text = entity_text.strip()
        
        # Check if LOCATION is actually a PARTY (person/company)
        if entity_type == 'LOCATION':
            person_patterns = [
                r',\s*(President|Vice|CEO|Director|Manager|Attorney|Counsel)',
                r'\b(Ltd|Inc|Corp|LLC|Company|Laboratories|Pharma|Funding|Finance|Commercial|Acquisition|Recovery|Solutions)\b',
                r'^[A-Z][a-z]+,\s+[A-Z][a-z]+',
                r'\b(Manager|By)\s+[A-Z]',
                r'\b(ACQUISITION|COMPUTER|ASTA|OPTION|PALISADES|RECOVERY)\s+[A-Z]+',
                r'\bFunding\b',
                r'\bFinance\b',
                r'\bCommercial\b'
            ]
            
            if any(re.search(pattern, text, re.IGNORECASE) for pattern in person_patterns):
                reclassified.append((entity_text, 'PARTY'))
                continue
        
        # Check if PARTY is actually an AGREEMENT_TYPE
        if entity_type == 'PARTY':
            agreement_keywords = ['agreement', 'contract', 'terms', 'conditions', 'protocol', 'memorandum', 'letter', 'commitment', 'loan', 'security']
            if any(keyword in text.lower() for keyword in agreement_keywords):
                reclassified.append((entity_text, 'AGREEMENT_TYPE'))
                continue
        
        # Check if LOCATION is actually an AGREEMENT_TYPE (less common but possible)
        if entity_type == 'LOCATION':
            agreement_keywords = ['agreement', 'contract', 'terms', 'conditions', 'protocol', 'memorandum', 'letter', 'commitment', 'loan', 'security']
            if any(keyword in text.lower() for keyword in agreement_keywords):
                reclassified.append((entity_text, 'AGREEMENT_TYPE'))
                continue
        
        reclassified.append((entity_text, entity_type))
    
    return reclassified

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_pdf_entities.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    
    print("🚀 CLEAN PDF to Entity Extraction Pipeline")
    print("=" * 50)
    
    # Check API
    try:
        health_response = requests.get('http://localhost:5002/health', timeout=5)
        if health_response.status_code != 200:
            print("❌ API not running. Start with: python api.py")
            return
        print("✅ API is running")
    except:
        print("❌ API not running. Start with: python api.py")
        return
    
    # Extract text
    print(f"📄 Processing: {pdf_path}")
    
    # Extract text directly using PyMuPDF
    print(f"📄 Extracting text from: {pdf_path}")
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        print(f"✅ Extracted {len(text)} characters")
        if len(text) < 100:
            print(f"📝 Preview: {text[:200]}...")
        return text
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return None

def extract_text_from_pdf_direct(pdf_path):
    """Extract text directly using PyMuPDF"""
    try:
        print(f"📄 Extracting text from: {pdf_path}")
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        print(f"✅ Extracted {len(text)} characters")
        if len(text) < 100:
            print(f"📝 Preview: {text[:200]}...")
        return text
    except Exception as e:
        print(f"❌ Text extraction failed: {e}")
        return None

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
    """Extract entities using running Docker API with chunking for long texts"""
    try:
        print("🌐 Sending to API...")
        
        # Check if text is too long and needs chunking
        max_chars = 10000
        if len(text) <= max_chars:
            # Send as single request
            response = requests.post('http://localhost:5002/extract', 
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
        else:
            # Split text into chunks
            print(f"📝 Text too long ({len(text)} chars), splitting into chunks...")
            chunks = []
            for i in range(0, len(text), max_chars):
                chunk = text[i:i + max_chars]
                chunks.append(chunk)
            
            print(f"📊 Processing {len(chunks)} chunks...")
            all_entities = []
            total_processing_time = 0
            
            for i, chunk in enumerate(chunks):
                print(f"🔄 Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                
                response = requests.post('http://localhost:5002/extract', 
                                       json={'text': chunk}, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    entities = result.get('entities', [])
                    processing_time = result.get('processing_time', 0.0)
                    
                    all_entities.extend(entities)
                    total_processing_time += processing_time
                    
                    print(f"✅ Chunk {i+1}: {len(entities)} entities")
                else:
                    print(f"❌ Chunk {i+1} failed: {response.status_code}")
                    print(f"📝 Error: {response.text}")
                    continue
            
            # Remove duplicates across chunks
            print("🧹 Removing duplicates across chunks...")
            unique_entities = []
            seen = set()
            
            for entity_text, entity_type in all_entities:
                key = (entity_text.strip().lower(), entity_type)
                if key not in seen:
                    seen.add(key)
                    unique_entities.append((entity_text, entity_type))
            
            print(f"✅ Total unique entities: {len(unique_entities)}")
            
            # Return combined result
            return {
                'entities': unique_entities,
                'entity_count': len(unique_entities),
                'processing_time': total_processing_time,
                'success': True,
                'timestamp': ''
            }
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return None

def extract_expiration_dates(entities: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Extract expiration dates from entities that contain expiration-related terms
    """
    expiration_entities = []
    
    for entity_text, entity_type in entities:
        text = entity_text.lower()
        
        # Look for expiration-related keywords
        expiration_keywords = ['expire', 'expiration', 'expired', 'expiring', 'expires']
        
        if any(keyword in text for keyword in expiration_keywords):
            # Try to extract date from the entity
            import re
            
            # Look for date patterns within the entity
            date_patterns = [
                r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}',
                r'\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',
                r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
                r'\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}',
                r'\b\d{4}\b'  # Just a year
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, entity_text)
                if match:
                    date_str = match.group()
                    # Clean up the date string
                    if len(date_str) >= 4:  # At least a year
                        expiration_entities.append((date_str, 'EXPIRATION_DATE'))
                        break
    
    return expiration_entities

def filter_important_entities(entities: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Filter to keep only the most important and relevant entities
    """
    important_entities = []
    
    # Words that should never be entities
    blacklist_words = {
        'representations', 'warranties', 'such', 'letters', 'numbers', 'hypothecated', 'assigned',
        'conveyed', 'transferred', 'lost', 'stolen', 'including', 'without', 'that',
        'whether', 'such', 'upon', 'shall', 'not', 'this', 'foregoing', 'than',
        'give', 'if', 'refusal', 'which', 'than', 'that', 'give', 'timely', 'basis',
        'counter', 'then', 'partnership', 'limited', 'liability', 'company', 'joint',
        'venture', 'trust', 'organization', 'business', 'individual', 'government',
        'requests', 'waivers', 'certified', 'mail', 'postage', 'prepaid', 'return',
        'receipt', 'requested', 'addressed', 'supplements', 'amendments', 'related',
        'definitions', 'all', 'county', 'any', 'action', 'suit', 'contemplated',
        'herein', 'except', 'terms', 'thereof', 'hurdle', 'or', 'less',
        'offered', 'shares', 'fair', 'otherwise', 'requires', 'comparable', 'section',
        'pursuant', 'hereto', 'respect', 'any', 'thereof', 'in', 'pursuant',
        'unconditionally', 'submits', 'for', 'itself', 'its', 'property', 'to',
        'judgment', 'each', 'such', 'action', 'proceeding', 'unconditionally',
        'waives', 'do', 'so', 'any', 'objection', 'irrevocably', 'waives',
        'accordance', 'lexington', 'evidenced', 'hereby', 'there', 'transfer',
        'taxes', 'authorization', 'execution', 'delivery', 'violation', 'constitute',
        'with', 'or', 'any', 'lien', 'charge', 'impairment', 'forfeiture',
        'material', 'permit', 'license', 'accordingly', 'purchased', 'hereunder',
        'when', 'issued', 'sold', 'expressed', 'will', 'offer', 'sale', 'change',
        'whatsoever', 'must', 'witness', 'whereof', 'parties', 'security',
        'exemption', 'from', 'or', 'in', 'subject', 'to', 'the', 'registration',
        'such', 'effect', 'the', 'substance', 'certificate', 'conditions', 'of',
        'and', 'may', 'exercise', 'price', 'at', 'surrendered', 'value',
        'received', 'foregoing', 'warrant', 'execute', 'alteration'
    }
    
    # Priority-based filtering
    for entity_text, entity_type in entities:
        text = entity_text.strip().lower()
        
        # Skip if contains blacklisted words
        if any(word in text.split() for word in blacklist_words):
            continue
        
        # Keep high-priority entities
        if entity_type == 'EFFECTIVE_DATE':
            # Keep complete dates, filter out fragments
            if re.search(r'\d{4}', entity_text) and len(entity_text) > 8:
                important_entities.append((entity_text, entity_type))
        
        elif entity_type == 'PARTY':
            # Keep proper company names and person names, filter generic terms
            company_indicators = ['LLC', 'Inc', 'Corp', 'Ltd', 'Company', 'Corporation', 'Group', 'Brothers', 'Funding', 'Finance']
            person_indicators = [r',\s*(President|Vice|CEO|Director|Manager|Attorney|Counsel|Esq)', r'\b(Manager|By)\s+[A-Z]']
            
            # Check if it's a company
            if any(indicator in entity_text for indicator in company_indicators):
                important_entities.append((entity_text, entity_type))
            # Check if it's a person
            elif any(re.search(pattern, entity_text, re.IGNORECASE) for pattern in person_indicators):
                important_entities.append((entity_text, entity_type))
            # Keep very short, specific party names (likely important)
            elif len(entity_text.split()) <= 3 and not entity_text.lower().startswith(('to ', 'of ', 'and ', 'in ', 'with ', 'as ', 'by ', 'for')):
                # Additional check for party names
                if any(word.isupper() for word in entity_text.split() if len(word) > 2):
                    important_entities.append((entity_text, entity_type))
        
        elif entity_type == 'AGREEMENT_TYPE':
            # Keep key agreement types, filter generic terms
            key_agreements = ['agreement', 'contract', 'warrant', 'security', 'loan', 'letter']
            if any(keyword in text for keyword in key_agreements):
                # Filter out very generic terms
                if len(entity_text) > 5 and not text in ['terms', 'conditions', 'provisions']:
                    important_entities.append((entity_text, entity_type))
        
        elif entity_type == 'LOCATION':
            # Keep specific locations, filter generic terms
            location_indicators = ['NY', 'NJ', 'USA', 'New York', 'California', 'Texas', 'Florida', 'Avenue', 'Street', 'Bay Shore']
            if any(indicator in entity_text for indicator in location_indicators):
                # Filter out very generic location descriptions
                if len(entity_text.split()) <= 4 and not any(word in text for word in ['terms', 'conditions', 'provisions', 'pursuant', 'accordance']):
                    important_entities.append((entity_text, entity_type))
        
        elif entity_type == 'AMOUNT':
            # Keep monetary amounts
            if re.search(r'\$[\d,]+\.?\d*', entity_text):
                important_entities.append((entity_text, entity_type))
        
        elif entity_type == 'DURATION':
            # Keep specific time periods
            if re.search(r'\d+\s+(days|months|years)', entity_text, re.IGNORECASE):
                important_entities.append((entity_text, entity_type))
    
    # Remove duplicates from filtered results
    final_entities = []
    seen = set()
    
    for entity_text, entity_type in important_entities:
        key = (entity_text.strip().lower(), entity_type)
        if key not in seen:
            seen.add(key)
            final_entities.append((entity_text, entity_type))
    
    return final_entities

def save_results(result, output_path, pdf_path):
    """Save results to JSON file with entity cleaning and importance filtering"""
    if result is None:
        print("❌ No results to save")
        return
    
    raw_entities = result.get('entities', [])
    
    # Clean and validate entities
    print(f"🧹 Cleaning {len(raw_entities)} raw entities...")
    cleaned_entities = clean_entities(raw_entities)
    
    # Reclassify misidentified entities
    print("🔄 Reclassifying misidentified entities...")
    reclassified_entities = reclassify_misidentified_entities(cleaned_entities)
    
    # Additional quality validation
    validated_entities = []
    for entity_text, entity_type in reclassified_entities:
        if validate_entity_quality(entity_text, entity_type):
            validated_entities.append((entity_text, entity_type))
    
    # Filter for most important entities
    print("⭐ Filtering for most important entities...")
    important_entities = filter_important_entities(validated_entities)
    
    # Extract expiration dates from the original entities
    print("📅 Extracting expiration dates...")
    expiration_dates = extract_expiration_dates(validated_entities)
    
    # Add expiration dates to the important entities
    all_entities = important_entities + expiration_dates
    
    # Remove any duplicates between important entities and expiration dates
    final_entities = []
    seen = set()
    
    for entity_text, entity_type in all_entities:
        key = (entity_text.strip().lower(), entity_type)
        if key not in seen:
            seen.add(key)
            final_entities.append((entity_text, entity_type))
    
    entity_count = len(final_entities)
    removed_count = len(raw_entities) - entity_count
    
    print(f"✅ Removed {removed_count} duplicate/invalid entities")
    print(f"✅ Kept {entity_count} high-quality important entities")
    if expiration_dates:
        print(f"📅 Found {len(expiration_dates)} expiration dates")
    
    output = {
        "source_file": pdf_path,
        "total_entities": entity_count,
        "raw_entities_count": len(raw_entities),
        "removed_entities_count": removed_count,
        "expiration_dates_found": len(expiration_dates),
        "entity_types": list(set(label for _, label in final_entities)),
        "entities": final_entities,
        "processing_method": "hybrid_with_cleaning_and_filtering",
        "processing_time": result.get('processing_time', 0.0),
        "success": result.get('success', False),
        "timestamp": result.get('timestamp', '')
    }
    
    output_file = output_path.replace('.pdf', '_entities.json')
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    print(f"📊 Total important entities: {entity_count}")
    print(f"🏷️  Entity types: {', '.join(output['entity_types'])}")
    
    if important_entities:
        print(f"\n📍 IMPORTANT ENTITIES:")
        for entity, label in important_entities:
            print(f"  {entity} → {label}")
    else:
        print(f"\n⚠️  No important entities found after filtering")

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_pdf_entities.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print("🚀 CLEAN PDF to Entity Extraction Pipeline")
    print("=" * 50)
    
    # Check if API is running
    try:
        health_response = requests.get('http://localhost:5002/health', timeout=5)
        if health_response.status_code != 200:
            print("❌ API is not running. Start Docker container first:")
            print("   docker start legal-ner-api")
            return
        print("✅ API is running")
    except:
        print("❌ API is not running. Start Docker container first:")
        print("   docker start legal-ner-api")
        return
    
    # Extract text from PDF using direct method
    text = extract_text_from_pdf_direct(pdf_path)
    if not text:
        print("❌ Failed to extract text from PDF")
        return
    
    # Extract entities via API
    result = extract_entities_via_api(text)
    if not result:
        print("❌ Failed to extract entities")
        return
    
    # Save results (only once at the end)
    save_results(result, pdf_path, pdf_path)
    
    print(f"\n🎉 SUCCESS! PDF → JSON pipeline complete!")
    print(f"📁 Check the JSON file for complete results")

if __name__ == "__main__":
    main()
