from ner_preprocessor import LegalNERPreprocessor
import json

def demo_model():
    """Demonstrate the NER model working on various examples"""
    
    print("🤖 LEGAL CONTRACT NER MODEL DEMO")
    print("=" * 50)
    
    # Initialize the model
    ner = LegalNERPreprocessor()
    print("✅ Model loaded successfully!")
    print(f"📋 Entity Types: {ner.nlp.get_pipe('ner').labels}")
    print()
    
    # Test cases showing different scenarios
    test_cases = [
        {
            "name": "Basic Agreement Detection",
            "text": "This loan agreement is made as of July 11, 2006 between ABC Corp and John Doe for $100,000."
        },
        {
            "name": "Date Format Variation", 
            "text": "This Agreement is effective from 12 January 2024 between ABC Pvt Ltd and John Doe."
        },
        {
            "name": "Multiple Entities",
            "text": "credit agreement dated December 31, 2008 between ASTA Funding and Mr. Stern for $500,000"
        },
        {
            "name": "Company Name Variation",
            "text": "security agreement effective January 15, 2024 between XYZ LLC and Jane Smith"
        },
        {
            "name": "Complex Legal Text",
            "text": "EXHIBIT 10.2 TECHNICAL SERVICES AGREEMENT This agreement is made on 4th day of October 2005 by and between Surgicenters of America, Inc. and Trillenium Medical Imaging for $1,200,000"
        }
    ]
    
    # Process each test case
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['name']}")
        print(f"Input: {test_case['text']}")
        
        # Extract entities
        result = ner.extract_entities(test_case['text'])
        
        print(f"Entities Found: {len(result['entities'])}")
        for entity in result['entities']:
            print(f"  • {entity[0]} → {entity[1]}")
        
        if not result['entities']:
            print("  ⚠️  No entities detected")
        
        print("-" * 50)
    
    # Summary statistics
    print("\n📊 SUMMARY")
    print("=" * 50)
    total_entities = sum(len(ner.extract_entities(tc['text'])['entities']) for tc in test_cases)
    print(f"Total test cases: {len(test_cases)}")
    print(f"Total entities detected: {total_entities}")
    print(f"Average entities per document: {total_entities/len(test_cases):.1f}")
    
    print("\n🎉 DEMO COMPLETE - Model is Working!")

if __name__ == "__main__":
    demo_model()
