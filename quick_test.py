from ner_preprocessor import LegalNERPreprocessor

# Quick usage
ner = LegalNERPreprocessor()

# Test your problematic text
text = "This Agreement is effective from 12 January 2024 between ABC Pvt Ltd and John Doe."
result = ner.extract_entities(text)

print("Input:", text)
print("Entities found:", result['entities'])

# You can also use it in your existing scripts:
# from ner_preprocessor import LegalNERPreprocessor
# ner = LegalNERPreprocessor()
# entities = ner.extract_entities(your_text)['entities']
