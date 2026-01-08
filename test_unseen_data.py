from hybrid_ner import HybridLegalNER
import random

def test_unseen_data():
    """Test the NER system on completely unseen legal text patterns"""
    
    print("🔍 TESTING ON UNSEEN DATA")
    print("=" * 60)
    
    # Initialize the system
    ner = HybridLegalNER()
    
    # Unseen test cases - different from training patterns
    unseen_tests = [
        {
            "name": "Employment Contract",
            "text": "This employment agreement is effective March 1, 2024 between TechStart Inc. and Sarah Johnson for annual salary $85,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "Real Estate Lease", 
            "text": "Commercial lease agreement dated June 15, 2023 between Property Management LLC and Tenant Corporation for monthly rent $5,500.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "Service Contract",
            "text": "Consulting services contract effective January 10, 2024 between Digital Solutions Ltd. and Michael Chen for project fee $25,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "Partnership Agreement",
            "text": "Partnership agreement formed November 30, 2023 between Anderson & Associates and Williams Group for initial capital $100,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "Complex Legal Text",
            "text": "WHEREAS, this master services agreement is executed on December 1, 2023 between Global Technology Solutions Inc., a Delaware corporation, and Client Company LLC, a New York limited liability company, for total contract value $2,500,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "Different Date Format",
            "text": "Supply agreement effective 5th February 2024 between Manufacturing Corp and Distributor Inc. for order amount $750,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "Financial Agreement",
            "text": "Loan facility agreement dated 20 March 2024 between First National Bank and Borrower Company Ltd for loan amount $10,000,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        },
        {
            "name": "International Contract",
            "text": "Distribution agreement effective 1 July 2024 between European Trading GmbH and American Export Corp for contract value €1,200,000.",
            "expected_entities": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
        }
    ]
    
    results = {
        "total_tests": len(unseen_tests),
        "successful_tests": 0,
        "total_expected_entities": 0,
        "total_detected_entities": 0,
        "entity_type_performance": {},
        "detailed_results": []
    }
    
    for i, test in enumerate(unseen_tests, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print(f"Text: {test['text']}")
        print("-" * 60)
        
        # Extract entities
        result = ner.extract_entities(test['text'])
        detected_entities = result['combined_entities']
        
        # Analyze results
        detected_types = {label for _, label in detected_entities}
        expected_types = set(test['expected_entities'])
        
        # Calculate success
        missing_types = expected_types - detected_types
        extra_types = detected_types - expected_types
        
        success = len(missing_types) == 0 and len(detected_entities) > 0
        
        if success:
            results["successful_tests"] += 1
        
        # Update counts
        results["total_expected_entities"] += len(expected_types)
        results["total_detected_entities"] += len(detected_entities)
        
        # Track entity type performance
        for expected_type in expected_types:
            if expected_type not in results["entity_type_performance"]:
                results["entity_type_performance"][expected_type] = {"found": 0, "total": 0}
            results["entity_type_performance"][expected_type]["total"] += 1
            if expected_type in detected_types:
                results["entity_type_performance"][expected_type]["found"] += 1
        
        # Display results
        print(f"Expected: {test['expected_entities']}")
        print(f"Detected: {[(ent, label) for ent, label in detected_entities]}")
        print(f"Status: {'✅ SUCCESS' if success else '❌ PARTIAL'}")
        
        if missing_types:
            print(f"Missing: {list(missing_types)}")
        if extra_types:
            print(f"Extra: {list(extra_types)}")
        
        # Store detailed result
        results["detailed_results"].append({
            "test_name": test['name'],
            "success": success,
            "expected": test['expected_entities'],
            "detected": [(ent, label) for ent, label in detected_entities],
            "missing": list(missing_types),
            "extra": list(extra_types)
        })
    
    # Calculate overall metrics
    success_rate = (results["successful_tests"] / results["total_tests"]) * 100
    entity_recall = (results["total_detected_entities"] / results["total_expected_entities"]) * 100 if results["total_expected_entities"] > 0 else 0
    
    print(f"\n🏁 UNSEEN DATA PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Successful Tests: {results['successful_tests']}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Entity Recall: {entity_recall:.1f}% ({results['total_detected_entities']}/{results['total_expected_entities']})")
    
    print(f"\n📊 Entity Type Performance:")
    for entity_type, perf in results["entity_type_performance"].items():
        type_success_rate = (perf["found"] / perf["total"]) * 100 if perf["total"] > 0 else 0
        print(f"  {entity_type}: {perf['found']}/{perf['total']} ({type_success_rate:.1f}%)")
    
    # Overall assessment
    if success_rate >= 70:
        assessment = "🟢 EXCELLENT - Handles unseen data very well"
    elif success_rate >= 50:
        assessment = "🟡 GOOD - Handles unseen data reasonably well"
    else:
        assessment = "🔴 NEEDS IMPROVEMENT - Struggles with unseen data"
    
    print(f"\n🎯 Overall Assessment: {assessment}")
    
    return results

if __name__ == "__main__":
    results = test_unseen_data()
    print(f"\n🎉 Unseen Data Testing Complete!")
