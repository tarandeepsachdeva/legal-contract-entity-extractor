from hybrid_ner import HybridLegalNER
import json

def comprehensive_demo():
    """Comprehensive demo showing ML vs Rules vs Hybrid"""
    
    print("🤖 COMPREHENSIVE HYBRID NER DEMO")
    print("=" * 60)
    
    # Initialize hybrid system
    hybrid_ner = HybridLegalNER()
    
    # Test cases with different complexity
    test_cases = [
        {
            "name": "Simple Legal Text",
            "text": "This loan agreement is made as of July 11, 2006 between ABC Corp and John Doe for $100,000."
        },
        {
            "name": "Complex Legal Document", 
            "text": "EXHIBIT 10.2 TECHNICAL SERVICES AGREEMENT This agreement is made on 4th day of October 2005 by and between Surgicenters of America, Inc. and Trillenium Medical Imaging for $1,200,000"
        },
        {
            "name": "Edge Case - Unseen Format",
            "text": "security agreement effective 15 January 2024 between XYZ LLC and Jane Smith amount 750000 USD"
        },
        {
            "name": "Multiple Entities",
            "text": "credit agreement dated December 31, 2008 between ASTA Funding and Mr. Stern for $500,000 expiring on December 31, 2015"
        }
    ]
    
    total_ml_entities = 0
    total_rule_entities = 0
    total_hybrid_entities = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Input: {test_case['text']}")
        print("-" * 60)
        
        # Get hybrid results (includes ML and rules comparison)
        result = hybrid_ner.extract_entities(test_case['text'], use_hybrid=True)
        
        ml_entities = result['ml_entities']
        rule_entities = result['rule_entities']
        hybrid_entities = result['combined_entities']
        
        # Display results
        print(f"🧠 ML Model Only:")
        if ml_entities:
            for entity, label in ml_entities:
                print(f"    • {entity} → {label}")
        else:
            print("    ❌ No entities detected")
        
        print(f"\n⚙️  Rules Only:")
        if rule_entities:
            for entity, label in rule_entities:
                print(f"    • {entity} → {label}")
        else:
            print("    ❌ No entities detected")
        
        print(f"\n🚀 Hybrid Combined:")
        if hybrid_entities:
            for entity, label in hybrid_entities:
                print(f"    • {entity} → {label}")
        else:
            print("    ❌ No entities detected")
        
        # Show improvement
        ml_count = len(ml_entities)
        rule_count = len(rule_entities)
        hybrid_count = len(hybrid_entities)
        
        print(f"\n📊 Comparison:")
        print(f"    ML Only: {ml_count} entities")
        print(f"    Rules: {rule_count} entities") 
        print(f"    Hybrid: {hybrid_count} entities")
        
        if hybrid_count > ml_count:
            improvement = ((hybrid_count - ml_count) / max(ml_count, 1)) * 100
            print(f"    🎯 Improvement: +{improvement:.0f}% over ML alone")
        
        # Update totals
        total_ml_entities += ml_count
        total_rule_entities += rule_count
        total_hybrid_entities += hybrid_count
        
        print("\n" + "="*60)
    
    # Final summary
    print(f"\n🏁 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total ML Entities: {total_ml_entities}")
    print(f"Total Rule Entities: {total_rule_entities}")
    print(f"Total Hybrid Entities: {total_hybrid_entities}")
    
    if total_hybrid_entities > total_ml_entities:
        overall_improvement = ((total_hybrid_entities - total_ml_entities) / max(total_ml_entities, 1)) * 100
        print(f"🎉 Overall Hybrid Improvement: +{overall_improvement:.0f}%")
    
    print(f"\n✅ Hybrid System Successfully Combines:")
    print(f"    🧠 Machine Learning (Context-aware)")
    print(f"    ⚙️  Rule-Based (High precision)")
    print(f"    🚀 Combined (Best of both)")

if __name__ == "__main__":
    comprehensive_demo()
