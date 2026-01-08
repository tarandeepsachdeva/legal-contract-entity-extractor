import requests
import json

def test_api():
    """Test the Legal NER API"""
    
    base_url = "http://localhost:5001"
    
    print("🧪 TESTING LEGAL NER API")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Model info
    print("\n2. Model Information")
    try:
        response = requests.get(f"{base_url}/info")
        print(f"✅ Status: {response.status_code}")
        info = response.json()
        print(f"Model Type: {info.get('model_type')}")
        print(f"Entity Labels: {info.get('entity_labels')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Single extraction
    print("\n3. Single Entity Extraction")
    test_text = "This loan agreement is made as of July 11, 2006 between ABC Corp and John Doe for $100,000."
    
    try:
        response = requests.post(f"{base_url}/extract", 
                               json={"text": test_text, "include_details": True})
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"Text: {result.get('text')}")
        print(f"Entities: {result.get('entities')}")
        print(f"Processing Time: {result.get('processing_time')}s")
        print(f"Method: {result.get('method')}")
        
        if result.get('ml_entities'):
            print(f"ML Entities: {result.get('ml_entities')}")
        if result.get('rule_entities'):
            print(f"Rule Entities: {result.get('rule_entities')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Batch extraction
    print("\n4. Batch Entity Extraction")
    test_texts = [
        "credit agreement dated December 31, 2008 between ASTA Funding and Mr. Stern for $500,000",
        "security agreement effective January 15, 2024 between XYZ LLC and Jane Smith amount 750000 USD",
        "EXHIBIT 10.2 TECHNICAL SERVICES AGREEMENT This agreement is made on 4th day of October 2005"
    ]
    
    try:
        response = requests.post(f"{base_url}/batch_extract", 
                               json={"texts": test_texts})
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"Batch Size: {result.get('batch_size')}")
        
        for i, item in enumerate(result.get('results', [])):
            print(f"  Text {i+1}: {item.get('success', False)} - {item.get('entity_count', 0)} entities")
            if item.get('entities'):
                print(f"    Entities: {item['entities']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Error handling
    print("\n5. Error Handling Test")
    try:
        response = requests.post(f"{base_url}/extract", json={"text": ""})
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"Error: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 API Testing Complete!")

if __name__ == "__main__":
    test_api()
