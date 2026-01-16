import spacy
from spacy.tokens import DocBin

nlp = spacy.blank("en")
db = DocBin().from_disk("../data/annotation/NER/spacy/admin3.spacy")

docs = list(db.get_docs(nlp.vocab))

print("Docs:", len(docs))
print("Entities in first doc:", docs[0].ents)
print([(ent.text, ent.label_) for ent in docs[0].ents])

