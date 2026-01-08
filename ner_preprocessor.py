import spacy
import re

class LegalNERPreprocessor:
    def __init__(self, model_path="training_output/best_model"):
        self.nlp = spacy.load(model_path)
    
    def normalize_text(self, text):
        """Normalize text to match training patterns"""
        # Date format normalization: "12 January 2024" -> "January 12, 2024"
        text = re.sub(r'(\d{1,2}) (\w+) (\d{4})', r'\2 \1, \3', text)
        
        # Date format normalization: "Jan 15, 2024" -> "January 15, 2024"
        month_map = {
            'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
            'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
            'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'
        }
        for short, full in month_map.items():
            text = re.sub(r'\b' + short + r'\b', full, text)
        
        # Agreement type normalization
        text = text.replace('Agreement', 'agreement')
        text = text.replace('Contract', 'agreement')
        text = text.replace('Pact', 'agreement')
        
        # Enhanced company name normalization - match training patterns
        text = re.sub(r'(\w+)\s+Pvt\s+Ltd', r'\1 Corp', text)
        text = re.sub(r'(\w+)\s+Limited', r'\1 Corp', text)
        text = re.sub(r'(\w+)\s+LLC', r'\1 Corp', text)
        text = re.sub(r'(\w+)\s+Inc\.', r'\1 Corp', text)
        text = re.sub(r'(\w+)\s+Inc', r'\1 Corp', text)
        
        # Add common patterns for party names based on training data
        # Normalize person names to match training patterns
        text = re.sub(r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b', r'\1 \2', text)
        
        # Add "and" between parties to match training patterns
        text = re.sub(r'(\w+\s+Corp)\s+(?:&|and)\s+(\w+\s+Corp)', r'\1 and \2', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_with_rules(self, text):
        """Add basic rule-based extraction for missing entities"""
        entities = []
        
        # TEMPORARILY DISABLED TO TEST
        # Very conservative PARTY patterns - only clear companies
        # party_patterns = [
        #     r'\b[A-Z][a-z]+\s+Inc\.?\b',
        #     r'\b[A-Z][a-z]+\s+Corp\.?\b', 
        #     r'\b[A-Z][a-z]+\s+LLC\b',
        #     r'\b[A-Z][a-z]+\s+Ltd\.?\b',
        #     r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+Inc\.?\b',
        #     r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+Corp\.?\b',
        #     r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+LLC\b',
        #     r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+Ltd\.?\b',
        # ]
        
        # for pattern in party_patterns:
        #     matches = re.finditer(pattern, text, re.IGNORECASE)
        #     for match in matches:
        #         party_name = match.group().strip()
                
        #         # Must contain clear company indicator
        #         company_indicators = ['Inc', 'Corp', 'LLC', 'Ltd']
                
        #         if any(indicator in party_name for indicator in company_indicators):
        #             entities.append((party_name, 'PARTY'))
        
        return entities
    
    def extract_entities(self, text):
        """Extract entities with preprocessing and basic rules"""
        # Normalize the text
        normalized_text = self.normalize_text(text)
        
        # Run NER on normalized text
        doc = self.nlp(normalized_text)
        
        # Get ML entities
        ml_entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Get rule-based entities for missing types
        rule_entities = self.extract_with_rules(text)
        
        # Combine and deduplicate
        all_entities = ml_entities + rule_entities
        seen_texts = set()
        final_entities = []
        
        for entity_text, label in all_entities:
            normalized = entity_text.lower().strip()
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                final_entities.append((entity_text, label))
        
        return {
            'original_text': text,
            'normalized_text': normalized_text,
            'entities': final_entities,
            'ml_entities': ml_entities,
            'rule_entities': rule_entities
        }

# Usage example
if __name__ == "__main__":
    # Initialize preprocessor
    ner = LegalNERPreprocessor()
    
    # Test with different formats
    test_texts = [
        "This Agreement is effective from 12 January 2024 between ABC Pvt Ltd and John Doe.",
        "credit agreement dated Dec 31, 2008 between ASTA Funding and Mr. Stern",
        "security agreement effective 15 January 2024 between XYZ LLC and Jane Smith"
    ]
    
    for text in test_texts:
        result = ner.extract_entities(text)
        print(f"Original: {result['original_text']}")
        print(f"Normalized: {result['normalized_text']}")
        print(f"Entities: {result['entities']}")
        print("-" * 50)
