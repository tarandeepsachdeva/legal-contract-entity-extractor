# Week 2: Data Annotation and Labeling (NER)

## Objective
The objective of Week 2 was to prepare a high-quality labeled dataset for a Named Entity Recognition (NER) task by manually annotating legal contract documents using the Doccano annotation tool.

---

## Tools Used
- **Doccano** (Web-based annotation tool)
- **Python Virtual Environment**
- **JSONL format** for data export

---

## Dataset Description
The dataset consists of legal contract documents collected in text format.  
These documents include employment agreements and related legal clauses.

The dataset contains:
- Digitally extracted text
- Text obtained from scanned documents (OCR output)

---

## Entity Labels Defined
The following entities were created and used for annotation:

- `AGREEMENT_TYPE`
- `PARTY`
- `EFFECTIVE_DATE`
- `EXPIRATION_DATE`
- `DURATION`
- `LOCATION`
- `AMOUNT`

---

## Annotation Process
1. A **Named Entity Recognition (NER)** project was created in Doccano.
2. Entity labels were configured according to legal contract requirements.
3. Text files were uploaded to the project dataset.
4. Manual annotation was performed by selecting relevant text spans and assigning appropriate entity labels.
5. Not all documents contained all entities; entities were labeled wherever applicable.
6. Annotation progress was tracked until completion.

---

## Annotation Output
After completing the annotation:
- The annotated data was exported from Doccano.
- The export format used was **JSON Lines (`.jsonl`)**, suitable for NLP model training.
- Each line in the file represents one annotated document with text and entity spans.

---

## Observations
- Some documents do not contain all entity types, which is expected in real-world legal data.
- Manual annotation improved understanding of entity boundaries and legal terminology.
- The annotated dataset is ready for use in model training.

---

## Outcome
By the end of Week 2:
- A fully annotated NER dataset was created.
- The dataset is structured and suitable for supervised learning.
- Week 2 objectives were successfully completed.

---

## Next Steps
- Use the annotated dataset for **NER model training** in Week 3.
- Apply machine learning or deep learning models for entity extraction.

---
INPUT_FILE = "data/annotation/NER/Doccano/admin.jsonl"
OUTPUT_FILE = "data/annotation/NER/spacy/train.jsonl"