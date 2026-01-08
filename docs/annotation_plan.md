# Annotation Plan – Legal Contract Entity Extractor

## Project Overview
This project focuses on extracting key legal entities from contractual documents using a Named Entity Recognition (NER) pipeline.  
Before training any model, high-quality manual annotation is required. This document describes the annotation strategy, entity definitions, and workflow.

---

## Objective of Annotation
The goal of annotation is to create labeled text data that will be used to train and evaluate an NER model capable of identifying important legal entities from both digital and scanned contracts.

---

## Data Sources
Annotated text is derived from OCR-processed and digitally extracted contract documents.

Source folders:
data/extracted_text/digital/
data/extracted_text/scanned/

After manual selection and trimming, annotation-ready text is stored in:
data/annotation_text/digital/
data/annotation_text/scanned/

---

## Selected Annotation Files

### Digital Contracts
- contract1_annot.txt  
- contract2_annot.txt  

### Scanned Contracts
- scanned1_annot.txt  
- scanned2.annot.txt  

These files contain concise, entity-rich paragraphs suitable for annotation.

---

## Entity Definitions
The following entities are annotated in the text:

| Entity Name        | Description |
|--------------------|-------------|
| AGREEMENT_TYPE     | Type of legal agreement (e.g., Warrant Agreement, Subscription Agreement) |
| PARTY              | Legal entities involved (companies, individuals, organizations) |
| EFFECTIVE_DATE     | Date when the agreement becomes effective |
| EXPIRATION_DATE    | Date when the agreement expires |
| DURATION           | Time period or validity duration of the agreement |

(Full definitions are maintained in `entity_definitions.md`.)

---

## Annotation Guidelines
- Annotate only **explicit mentions** present in the text.
- Do not infer missing information.
- Dates should be annotated exactly as written.
- Blank placeholders (e.g., “___ day of ___”) are not annotated.
- Maintain consistency across all files.

---

## Annotation Tool
Annotations will be performed using **Doccano**, an open-source data annotation platform.

Tool features used:
- Named Entity Recognition (NER) labeling
- Manual span selection
- Export to JSON format

---

## Output Format
Annotated data will be exported from Doccano in **JSON format**, which will later be converted into training-ready formats compatible with SpaCy or BiLSTM models.

---

## Scope Limitation
This annotation phase focuses on **quality over quantity**.  
A small but accurate annotated dataset is sufficient for demonstrating the complete NER pipeline for this internship project.

---

## Next Steps
- Upload annotation files to Doccano
- Perform manual entity labeling
- Export annotated data
- Begin NER model training (Week 3)
