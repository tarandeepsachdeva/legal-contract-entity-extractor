#!/usr/bin/env python3
"""
Test the entity cleaning function on existing problematic data
"""

import json
import sys
import os

# Add the current directory to the path to import from clean_pdf_entities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_pdf_entities import clean_entities, validate_entity_quality, reclassify_misidentified_entities

def test_cleaning():
    """Test the cleaning functions on the problematic digital_pdf22 data"""
    
    # Load the problematic data
    with open('data/raw pdfs/Digital/digital_pdf22_entities.json', 'r') as f:
        data = json.load(f)
    
    raw_entities = data['entities']
    
    print("🔍 TESTING ENTITY CLEANING")
    print("=" * 50)
    print(f"Original entities: {len(raw_entities)}")
    print()
    
    # Show some problematic examples
    print("❌ PROBLEMATIC ENTITIES (Original):")
    problem_examples = [
        ("November 30, 2004", "EFFECTIVE_DATE"),
        ("November  30,  2004", "EFFECTIVE_DATE"),  # duplicate with extra spaces
        ("to that certain", "PARTY"),  # generic phrase
        ("Acquisition, Testing", "LOCATION"),  # misclassified
        ("Handley, President", "LOCATION"),  # should be PARTY
        ("DEVELOPMENT AGREEMENT", "AGREEMENT_TYPE"),
        ("Development \nAgreement", "AGREEMENT_TYPE"),  # duplicate with newline
    ]
    
    for text, label in problem_examples:
        if (text, label) in raw_entities:
            print(f"  '{text}' → {label}")
    
    print()
    
    # Apply cleaning
    print("🧹 APPLYING CLEANING...")
    cleaned_entities = clean_entities(raw_entities)
    print(f"After basic cleaning: {len(cleaned_entities)}")
    
    # Apply reclassification
    print("🔄 RECLASSIFYING MISIDENTIFIED ENTITIES...")
    reclassified_entities = reclassify_misidentified_entities(cleaned_entities)
    print(f"After reclassification: {len(reclassified_entities)}")
    
    # Show reclassification changes
    changes = []
    for (clean_text, clean_type), (reclass_text, reclass_type) in zip(cleaned_entities, reclassified_entities):
        if clean_type != reclass_type:
            changes.append(f"'{clean_text}': {clean_type} → {reclass_type}")
    
    if changes:
        print("Reclassifications made:")
        for change in changes:
            print(f"  {change}")
    
    # Apply validation
    validated_entities = []
    for entity_text, entity_type in reclassified_entities:
        if validate_entity_quality(entity_text, entity_type):
            validated_entities.append((entity_text, entity_type))
    
    print(f"After validation: {len(validated_entities)}")
    print(f"Removed: {len(raw_entities) - len(validated_entities)} entities")
    print()
    
    # Show final results
    print("✅ CLEANED ENTITIES:")
    if validated_entities:
        for entity, label in validated_entities:
            print(f"  '{entity}' → {label}")
    else:
        print("  No valid entities found!")
    
    print()
    
    # Show entity type distribution
    type_counts = {}
    for _, label in validated_entities:
        type_counts[label] = type_counts.get(label, 0) + 1
    
    print("📊 ENTITY TYPE DISTRIBUTION:")
    for entity_type, count in type_counts.items():
        print(f"  {entity_type}: {count}")

if __name__ == "__main__":
    test_cleaning()
