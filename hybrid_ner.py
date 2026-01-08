import spacy
import re
from ner_preprocessor import LegalNERPreprocessor

class HybridLegalNER:
    def __init__(self, model_path="training_output/best_model"):
        self.nlp = spacy.load(model_path)
        self.preprocessor = LegalNERPreprocessor(model_path)
    
    def extract_with_rules(self, text):
        """Rule-based extraction for high-precision patterns"""
        entities = []
        
        # Amount patterns (very high precision)
        amount_patterns = [
            r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:billion|million|thousand|trillion|hundred))?',
            r'\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:billion|million|thousand|trillion|hundred)?\s*(?:USD|dollars?)',
            r'(?:USD|\$)\s*\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:billion|million|thousand|trillion|hundred))?',
            r'\d+(?:\.\d+)?\s*(?:billion|million|thousand|trillion|hundred)\s+(?:USD|dollars?)',
            r'(?:USD|\$)\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?'
        ]
        
        for pattern in amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'AMOUNT'))
        
        # Date patterns
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b',
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s*\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b(?:\s+and\s+|\s+until\s+|\s+terminate[sd]?\s+|\s+effective\s+)',
            r'\b(?:as\s+of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'EFFECTIVE_DATE'))
        
        # Expiration date patterns
        expiration_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b(?:\s+and\s+|\s+until\s+|\s+terminate[sd]?\s+)',
            r'\b(?:expire[sd]?|terminate[sd]?|end[sd]?)\s+(?:on\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b(?:\s+and\s+|\s+until\s+|\s+terminate[sd]?\s+)'
        ]
        
        for pattern in expiration_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'EXPIRATION_DATE'))
        
        # Agreement type patterns (more precise)
        agreement_patterns = [
            r'\b[A-Z]*[a-z]*\s*agreement\b',
            r'\b[A-Z]*[a-z]*\s*contract\b',
            r'\b[A-Z]*[a-z]*\s*pact\b',
            r'\b[A-Z]*[a-z]*\s*understanding\b',
            r'\b[A-Z]*[a-z]*\s*memorandum\b',
            r'\b[A-Z]*[a-z]*\s*letter\s+(?:agreement|contract|understanding)\b',
            r'\b[A-Z]*[a-z]*\s*protocol\b',
            r'\b[A-Z]*[a-z]*\s*arrangement\b',
            r'\b[A-Z]*[a-z]*\s*commitment\b',
            r'\b[A-Z]*[a-z]*\s*instrument\b',
            r'\b[A-Z]*[a-z]*\s*settlement\b',
            r'\b[A-Z]*[a-z]*\s*accord\b',
            r'\b[A-Z]*[a-z]*\s*covenant\b',
            r'\b[A-Z]*[a-z]*\s*deed\b',
            r'\b[A-Z]*[a-z]*\s*indenture\b',
            r'\b[A-Z]*[a-z]*\s*prospectus\b',
            r'\b[A-Z]*[a-z]*\s*statement\s+(?:of\s+additional\s+information)?\b',
            r'\b[A-Z]*[a-z]*\s*policy\b',
            r'\b[A-Z]*[a-z]*\s*terms\s+(?:and\s+conditions)?\b'
        ]
        
        for pattern in agreement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'AGREEMENT_TYPE'))
        
        # Location patterns (more precise)
        location_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*[A-Z][A-Z]+\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\b(?:New\s+York|Los\s+Angeles|Chicago|Houston|Phoenix|Philadelphia|San\s+Antonio|San\s+Diego|Dallas|San\s+Jose|Austin|Jacksonville|Fort\s+Worth|Columbus|Charlotte|San\s+Francisco|Indianapolis|Seattle|Denver|Washington|Boston|El\s+Paso|Nashville|Detroit|Oklahoma\s+City|Portland|Las\s+Vegas|Baltimore|Memphis|Milwaukee|Tucson|Fresno|Sacramento|Kansas\s+City|Mesa|Atlanta|Omaha|Colorado\s+Springs|Raleigh|Long\s+Beach|Virginia\s+Beach|Miami|Oakland|Minneapolis|Tampa|Tulsa|Arlington|Wichita|New\s+Orleans|Bakersfield|Honolulu|Anaheim|Santa\s+Ana|Riverside|Corona|Lexington|Stockton|Cincinnati|Irvine|Greensboro|Lincoln|Toledo|St.\s+Louis|Rochester|Newark|Plano|Durham|St.\s+Paul|Orlando|Laredo|Chula\s+Vista|Madison|Gilbert|Buffalo|Chandler|Glendale|North\s+Las\s+Vegas|Scottsdale|Reno|Henderson|Jersey\s+City|Chesapeake|Garland|Irving|Fremont|Norfolk|Boise|Richmond|Spokane|Baton\s+Rouge)\b',
            r'\b(?:United\s+States|U\.S\.A\.|USA|Canada|UK|United\s+Kingdom|Germany|France|Japan|China|India|Australia|Mexico|Brazil|Argentina|Spain|Italy|Netherlands|Switzerland|Sweden|Norway|Denmark|Finland|Belgium|Austria|Poland|Czech\s+Republic|Hungary|Romania|Bulgaria|Greece|Portugal|Turkey|Russia|Ukraine|Belarus|Estonia|Latvia|Lithuania|Moldova|Slovakia|Slovenia|Croatia|Bosnia|Serbia|Montenegro|Albania|Macedonia|Kosovo|Cyprus|Malta|Luxembourg|Monaco|Andorra|Liechtenstein|Vatican\s+City|San\s+Marino|Iceland|Ireland|Northern\s+Ireland|Scotland|Wales|England|Great\s+Britain)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'LOCATION'))
        
        # Duration patterns (more precise)
        duration_patterns = [
            r'\b\d+(?:\.\d+)?\s*(?:years?|yrs?)\b(?!\s+of\s+age)',
            r'\b\d+(?:\.\d+)?\s*(?:months?|mos?)\b(?!\s+of\s+age)',
            r'\b\d+(?:\.\d+)?\s*(?:weeks?|wks?)\b(?!\s+of\s+age)',
            r'\b\d+(?:\.\d+)?\s*(?:days?)\b(?!\s+of\s+age)',
            r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(?:years?|yrs?)\b',
            r'\b(?:per\s+annum|annually|yearly|monthly|quarterly|weekly|daily)\b(?!\s+of\s+age)'
        ]
        
        for pattern in duration_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'DURATION'))
        
        # Percentage patterns
        percentage_patterns = [
            r'\b\d+(?:\.\d+)?\s*%\b',
            r'\b\d+(?:\.\d+)?\s*percent\b',
            r'\b\d+(?:\.\d+)?\s*percentage\b'
        ]
        
        for pattern in percentage_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append((match.group().strip(), 'PERCENTAGE'))
        
        # PARTY patterns - comprehensive
        party_patterns = [
            # Company names with indicators
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Inc\.?|Corp\.?|LLC|Ltd\.?|L\.P\.?|PLC|Group|Holdings|Company|Corporation|Trust|Fund)\b',
            r'\b[A-Z][a-z]+\s+(?:Management|Advisors|Investments|Financial|Capital|Global|International|National|American|First|Second|Third)\s+(?:Inc\.?|Corp\.?|LLC|Ltd\.?)\b',
            # Person names (legal documents)
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Jr\.?|Sr\.?|II|III|IV|Esq\.?)\b',
            r'\b[A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+\b',
            # Trust and Fund names
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Trust|Fund|Foundation|Endowment)\b',
            # Clear party indicators
            r'\bbetween\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'\bby\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        ]
        
        for pattern in party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                party_name = match.group().strip()
                
                # Enhanced validation for different party types
                company_indicators = ['Inc', 'Corp', 'LLC', 'Ltd', 'L.P.', 'PLC', 'Group', 'Holdings', 'Company', 'Corporation', 'Trust', 'Fund']
                person_indicators = ['Jr', 'Sr', 'II', 'III', 'IV', 'Esq', 'Inc', 'Corp']
                trust_indicators = ['Trust', 'Fund', 'Foundation', 'Endowment']
                
                # Accept if it has clear indicators or is a proper name pattern
                if (any(indicator in party_name for indicator in company_indicators) or
                    any(indicator in party_name for indicator in person_indicators) or
                    any(indicator in party_name for indicator in trust_indicators) or
                    'between' in party_name or 'to' in party_name or 'by' in party_name):
                    entities.append((party_name, 'PARTY'))
        
        return entities
    
    def extract_entities(self, text, use_hybrid=True):
        """Hybrid extraction combining ML and rules"""
        if use_hybrid:
            # Get ML predictions
            ml_result = self.preprocessor.extract_entities(text)
            ml_entities = ml_result['entities']
            
            # Get rule-based predictions
            rule_entities = self.extract_with_rules(text)
            
            # Combine and deduplicate
            all_entities = ml_entities + rule_entities
            
            # Remove duplicates (keep ML version if conflict)
            seen_texts = set()
            final_entities = []
            
            for entity_text, label in all_entities:
                # Normalize for comparison
                normalized_text = entity_text.lower().strip()
                if normalized_text not in seen_texts:
                    seen_texts.add(normalized_text)
                    final_entities.append((entity_text, label))
            
            return {
                'original_text': text,
                'normalized_text': ml_result['normalized_text'],
                'ml_entities': ml_entities,
                'rule_entities': rule_entities,
                'combined_entities': final_entities,
                'total_entities': len(final_entities)
            }
        else:
            # ML only
            return self.preprocessor.extract_entities(text)

# Demo the hybrid approach
if __name__ == "__main__":
    print("🤖 HYBRID LEGAL NER DEMO")
    print("=" * 50)
    
    hybrid_ner = HybridLegalNER()
    
    test_texts = [
        "This loan agreement is made as of July 11, 2006 between ABC Corp and John Doe for $100,000.",
        "credit agreement dated December 31, 2008 between ASTA Funding and Mr. Stern for $500,000",
        "security agreement effective 15 January 2024 between XYZ LLC and Jane Smith amount 750000 USD"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}:")
        print(f"Input: {text}")
        
        # ML only
        ml_only = hybrid_ner.extract_entities(text, use_hybrid=False)
        print(f"ML Only: {ml_only['entities']} ({len(ml_only['entities'])} entities)")
        
        # Hybrid
        hybrid = hybrid_ner.extract_entities(text, use_hybrid=True)
        print(f"Hybrid: {hybrid['combined_entities']} ({hybrid['total_entities']} entities)")
        print(f"  + Rules added: {len(hybrid['rule_entities'])}")
        print("-" * 50)
