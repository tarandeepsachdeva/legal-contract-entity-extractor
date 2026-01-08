# Week 1 – PDF Text Extraction & OCR Pipeline

## Objective
The objective of Week 1 is to build a robust data ingestion pipeline capable of handling both **digital** and **scanned** legal contract PDFs. The extracted text will be cleaned and stored for downstream NLP tasks such as Named Entity Recognition (NER).

---

## Dataset Description
- Digital PDFs: Text-selectable legal contracts
- Scanned PDFs: Image-based contracts requiring OCR
- Total documents: Small representative dataset (used for proof-of-concept)

The dataset intentionally includes both formats to demonstrate real-world document variability.

---

## Pipeline Overview

PDF → OCR/Text Extraction → Text Cleaning → Stored `.txt` Files

### High-Level Flow
Raw PDF
├── Digital PDF → Direct Text Extraction (PyMuPDF)
└── Scanned PDF → OCR (Tesseract)
↓
Raw Extracted Text
↓
Text Cleaning & Normalization
↓
Cleaned Text Files (.txt)

## Pipeline Components

### 1. Digital PDF Text Extraction
- Tool: **PyMuPDF**
- Purpose: Extract embedded text directly without OCR
- Benefit: Faster and cleaner extraction

### 2. Scanned PDF OCR
- Tools:
  - `pdf2image` for PDF-to-image conversion
  - `Tesseract OCR` for text recognition
- Purpose: Handle image-only documents
- Note: OCR output may contain noise (expected behavior)

### 3. Text Cleaning
Performed to improve downstream NLP performance:
- Convert text to lowercase
- Normalize whitespace
- Remove non-ASCII characters
- Preserve paragraph structure where possible

This step ensures consistency across digital and scanned documents.

### 4. Batch Processing
- All PDFs are processed automatically
- Files are routed based on folder name (`Digital` / `Scanned`)
- Cleaned text is saved with metadata

---

## Project Folder Structure
project/
├── data/
│ ├── raw_pdfs/
│ │ ├── Digital/
│ │ └── Scanned/
│ └── extracted_text/
│ ├── digital/
│ └── scanned/
│
├── src/
│ ├── ocr/
│ │ ├── pdf_text.py
│ │ ├── OCR_extractor.py
│ │ └── text_cleaning.py
│ └── opera_run.py
│
└── docs/
└── Week-1.md

---

## Output Format
Each processed PDF produces a `.txt` file containing:
- Source type (digital or scanned)
- Cleaned extracted text

Example:
SOURCE_TYPE: scanned
this agreement is made on december 31, 2008 between...

---





---

## Next Steps (Week 2)
- Manual annotation of selected documents
- Train a Named Entity Recognition (NER) model
- Extract key legal entities such as parties, dates, and monetary values