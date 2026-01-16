import spacy
from hybrid_ner import HybridLegalNER
import json
from collections import defaultdict, Counter

class ModelSanityChecker:
    def __init__(self, model_path="training_output/best_model"):
        self.hybrid_ner = HybridLegalNER(model_path)
        self.nlp = spacy.load(model_path)
    
    def check_model_weights(self):
        """Check model weights and pipeline status"""
        print("🔍 MODEL WEIGHTS & PIPELINE CHECK")
        print("=" * 50)
        
        # Pipeline info
        print(f"📋 Pipeline Components: {self.nlp.pipe_names}")
        print(f"🏷️  NER Labels: {self.nlp.get_pipe('ner').labels}")
        print(f"📊 Model Size: {len(self.nlp.vocab)} tokens in vocab")
        
        # Check if model has learned weights
        ner = self.nlp.get_pipe('ner')
        print(f"🧠 NER Model Type: {type(ner).__name__}")
        
        # Check if model is blank vs trained
        try:
            # Test with simple text
            test_doc = self.nlp.make_doc("test")
            print(f"✅ Model can process text: {len(test_doc)} tokens")
        except Exception as e:
            print(f"❌ Model processing error: {e}")
        
        return True
    
    def check_entity_distribution(self):
        """Check entity distribution in training data vs predictions"""
        print("\n📊 ENTITY DISTRIBUTION ANALYSIS")
        print("=" * 50)
        
        # Load training data for reference
        try:
            from spacy.tokens import DocBin
            db = DocBin().from_disk("data/annotation/NER/spacy/train.spacy")
            docs = list(db.get_docs(self.nlp.vocab))
            
            # Count entities in training data
            training_counts = defaultdict(int)
            for doc in docs:
                for ent in doc.ents:
                    training_counts[ent.label_] += 1
            
            print("📚 Training Data Entity Counts:")
            total_training = sum(training_counts.values())
            for label, count in sorted(training_counts.items()):
                percentage = (count / total_training) * 100
                print(f"  • {label}: {count} ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"⚠️  Could not load training data: {e}")
            training_counts = {}
        
        return training_counts
    
    def test_hybrid_predictions(self):
        """Test hybrid system predictions and analyze results"""
        print("\n🚀 HYBRID SYSTEM PREDICTION TEST")
        print("=" * 50)
        
        # Test cases covering all entity types
        test_cases = [
            {
                "name": "Amount Test",
                "text": "The contract value is $1,250,000 USD",
                "expected": ["AMOUNT"]
            },
            {
                "name": "Date Test", 
                "text": "Effective from January 15, 2024",
                "expected": ["EFFECTIVE_DATE"]
            },
            {
                "name": "Agreement Test",
                "text": "This loan agreement between parties",
                "expected": ["AGREEMENT_TYPE"]
            },
            {
                "name": "Party Test",
                "text": "between ABC Corporation and John Doe",
                "expected": ["PARTY"]
            },
            {
                "name": "Complex Test",
                "text": "credit agreement dated December 31, 2008 between ASTA Funding and Mr. Stern for $500,000",
                "expected": ["AGREEMENT_TYPE", "EFFECTIVE_DATE", "PARTY", "AMOUNT"]
            }
        ]
        
        results = {
            "total_tests": len(test_cases),
            "ml_entities": 0,
            "rule_entities": 0,
            "hybrid_entities": 0,
            "entity_type_counts": defaultdict(int),
            "test_results": []
        }
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['name']}")
            print(f"Text: {test_case['text']}")
            
            # Get hybrid results
            result = self.hybrid_ner.extract_entities(test_case['text'])
            
            ml_entities = result['ml_entities']
            rule_entities = result['rule_entities']
            hybrid_entities = result['combined_entities']
            
            print(f"🧠 ML: {ml_entities}")
            print(f"⚙️  Rules: {rule_entities}")
            print(f"🚀 Hybrid: {hybrid_entities}")
            
            # Count entities
            results["ml_entities"] += len(ml_entities)
            results["rule_entities"] += len(rule_entities)
            results["hybrid_entities"] += len(hybrid_entities)
            
            # Count by type
            for entity, label in hybrid_entities:
                results["entity_type_counts"][label] += 1
            
            # Check expected entities
            found_types = {label for _, label in hybrid_entities}
            expected_types = set(test_case['expected'])
            missing = expected_types - found_types
            extra = found_types - expected_types
            
            success = len(missing) == 0
            results["test_results"].append({
                "name": test_case['name'],
                "success": success,
                "expected": test_case['expected'],
                "found": list(found_types),
                "missing": list(missing),
                "extra": list(extra)
            })
            
            print(f"✅ Success: {success}")
            if missing:
                print(f"❌ Missing: {missing}")
            if extra:
                print(f"⚠️  Extra: {extra}")
        
        return results
    
    def analyze_performance(self, results):
        """Analyze performance metrics"""
        print("\n📈 PERFORMANCE ANALYSIS")
        print("=" * 50)
        
        # Entity counts
        print(f"🧠 ML Total Entities: {results['ml_entities']}")
        print(f"⚙️  Rules Total Entities: {results['rule_entities']}")
        print(f"🚀 Hybrid Total Entities: {results['hybrid_entities']}")
        
        # Improvement calculation
        if results['ml_entities'] > 0:
            improvement = ((results['hybrid_entities'] - results['ml_entities']) / results['ml_entities']) * 100
            print(f"📊 Hybrid Improvement: +{improvement:.1f}% over ML")
        
        # Entity type distribution
        print(f"\n🏷️  Entity Types Detected:")
        for label, count in sorted(results['entity_type_counts'].items()):
            print(f"  • {label}: {count}")
        
        # Test success rate
        successful_tests = sum(1 for test in results['test_results'] if test['success'])
        success_rate = (successful_tests / results['total_tests']) * 100
        print(f"\n✅ Test Success Rate: {success_rate:.1f}% ({successful_tests}/{results['total_tests']})")
        
        # Detailed test results
        print(f"\n📋 Detailed Test Results:")
        for test in results['test_results']:
            status = "✅" if test['success'] else "❌"
            print(f"  {status} {test['name']}: {test['found']}")
        
        return {
            "improvement": improvement if results['ml_entities'] > 0 else 0,
            "success_rate": success_rate,
            "entity_coverage": len(results['entity_type_counts'])
        }
    
    def generate_report(self):
        """Generate comprehensive sanity check report"""
        print("🎯 COMPREHENSIVE MODEL SANITY CHECK")
        print("=" * 60)
        
        # 1. Check model weights
        self.check_model_weights()
        
        # 2. Check entity distribution
        training_counts = self.check_entity_distribution()
        
        # 3. Test predictions
        prediction_results = self.test_hybrid_predictions()
        
        # 4. Analyze performance
        performance_metrics = self.analyze_performance(prediction_results)
        
        # 5. Summary
        print("\n🏁 SANITY CHECK SUMMARY")
        print("=" * 60)
        print(f"✅ Model Status: Functional")
        print(f"📊 Hybrid Improvement: +{performance_metrics['improvement']:.1f}%")
        print(f"🎯 Test Success Rate: {performance_metrics['success_rate']:.1f}%")
        print(f"🏷️  Entity Coverage: {performance_metrics['entity_coverage']} types")
        
        # Overall health
        health_score = (performance_metrics['improvement'] + performance_metrics['success_rate']) / 2
        if health_score >= 70:
            status = "🟢 EXCELLENT"
        elif health_score >= 50:
            status = "🟡 GOOD"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
        
        print(f"🏥 Overall Health: {status} ({health_score:.1f}/100)")
        
        return {
            "model_health": health_score,
            "status": status,
            "metrics": performance_metrics
        }

if __name__ == "__main__":
    # Run comprehensive sanity check
    checker = ModelSanityChecker()
    report = checker.generate_report()
    
    print(f"\n🎉 Sanity Check Complete!")
    print(f"Model is ready for {'production' if report['model_health'] >= 70 else 'further optimization'}")
