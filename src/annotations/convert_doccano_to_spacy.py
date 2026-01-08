import json
import spacy
from spacy.tokens import DocBin

INPUT_FILE = "../data/annotation/NER/Doccano/admin3.jsonl"
OUTPUT_FILE = "../data/annotation/NER/spacy/admin3.spacy"

nlp = spacy.blank("en")
db = DocBin()

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        text = item["text"]
        labels = item.get("label", [])

        doc = nlp.make_doc(text)
        ents = []

        for start, end, label in labels:
            span = doc.char_span(start, end, label=label)
            if span:
                ents.append(span)

        doc.ents = ents
        db.add(doc)

db.to_disk(OUTPUT_FILE)
print("✅ Conversion complete. spaCy file saved.")
