the commits were added recently because of github account issue so pls ignore those commits.

# Legal Contract Entity Extractor

Complete pipeline for extracting entities from legal PDF documents using NER.

## Overview

End-to-end system for:
- PDF text extraction (digital & scanned)
- Entity annotation with Doccano
- Model training with spaCy
- Testing and validation

## Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Poppler & Tesseract (for OCR)

## Installation

### 1. System Dependencies

**Windows:**
```powershell
# Install Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Poppler and Tesseract
choco install poppler tesseract

# Add to PATH (if not automatically added)
# C:\ProgramData\chocolatey\lib\poppler\tools\poppler-xx\bin
# C:\ProgramData\chocolatey\lib\tesseract\tools\tesseract
```

**Alternative Windows Installation:**
```powershell
# Download and install manually:
# Poppler: https://github.com/oschwartz10612/poppler-windows/releases/
# Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

# Add installation directories to Windows PATH
```

**macOS:**
```bash
brew install poppler tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils tesseract-ocr
```

### 2. Python Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Docker Setup

**Windows:**
```powershell
# Build NER API container
docker build -t legal-ner-api .

# Start container
docker run -p 5001:5001 --name legal-ner-api legal-ner-api

# Or use docker-compose
docker-compose up -d
```

**Linux/macOS:**
```bash
# Build NER API container
docker build -t legal-ner-api .

# Start container
docker run -p 5001:5001 --name legal-ner-api legal-ner-api

# Or use docker-compose
docker-compose up -d
```

## Project Structure

```
├── data/
│   ├── raw pdfs/              # Input PDFs
│   ├── annotation/NER/        # Doccano exports & spaCy data
│   │   ├── Doccano/          # Raw annotations
│   │   └── spacy/            # spaCy training format
│   └── models/               # Trained models
├── src/
│   └── annotations/          # Conversion scripts
├── training_output/          # Model training results
├── docs/                     # Documentation
├── clean_pdf_entities.py     # Main extraction script
├── train_config.py          # Training configuration
└── requirements.txt
```

## Pipeline Steps

### Step 1: PDF Text Extraction

**Windows:**
```powershell
# Digital PDF
python clean_pdf_entities.py "data\raw pdfs\Digital\example.pdf"

# Scanned PDF (with OCR)
python clean_pdf_entities.py "data\raw pdfs\Scanned\example.pdf"
```

**Linux/macOS:**
```bash
# Digital PDF
python clean_pdf_entities.py "data/raw pdfs/Digital/example.pdf"

# Scanned PDF (with OCR)
python clean_pdf_entities.py "data/raw pdfs/Scanned/example.pdf"
```

**Output:** `example_entities.json` with extracted entities

### Step 2: Entity Annotation with Doccano

1. **Start Doccano:**
```powershell
# Windows
docker-compose up -d

# Linux/macOS
docker-compose up -d
```

2. **Access:** http://localhost:8000
3. **Import Data:** Upload extracted text from Step 1
4. **Annotate:** Label entities (PARTY, DATE, LOCATION, etc.)
5. **Export:** Download as JSONL format

### Step 3: Convert to spaCy Format

**Windows:**
```powershell
python src\annotations\convert_doccano_to_spacy.py `
  --input data\annotation\NER\Doccano\annotated.jsonl `
  --output data\annotation\NER\spacy\training_data.spacy `
  --format spacy
```

**Linux/macOS:**
```bash
python src/annotations/convert_doccano_to_spacy.py \
  --input data/annotation/NER/Doccano/annotated.jsonl \
  --output data/annotation/NER/spacy/training_data.spacy \
  --format spacy
```

### Step 4: Model Training

**Windows:**
```powershell
python train_config.py `
  --train-data data\annotation\NER\spacy\train.spacy `
  --dev-data data\annotation\NER\spacy\val.spacy `
  --output training_output\legal_ner_model `
  --n-iter 100
```

**Linux/macOS:**
```bash
python train_config.py \
  --train-data data/annotation/NER/spacy/train.spacy \
  --dev-data data/annotation/NER/spacy/val.spacy \
  --output training_output/legal_ner_model \
  --n-iter 100
```

### Step 5: Testing & Validation

**Windows:**
```powershell
# Test on new documents
python clean_pdf_entities.py "data\raw pdfs\test_document.pdf"

# Validation metrics (if available)
python -c "import spacy; nlp = spacy.load('training_output\legal_ner_model'); print('Model loaded successfully')"
```

**Linux/macOS:**
```bash
# Test on new documents
python clean_pdf_entities.py "data/raw pdfs/test_document.pdf"

# Validation metrics (if available)
python -c "import spacy; nlp = spacy.load('training_output/legal_ner_model'); print('Model loaded successfully')"
```

## Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| PARTY | Companies, people | "ACME Corp", "John Doe" |
| EFFECTIVE_DATE | Agreement dates | "January 1, 2023" |
| LOCATION | Addresses, places | "New York, NY" |
| AGREEMENT_TYPE | Document types | "Loan Agreement" |
| AMOUNT | Monetary values | "$1,000,000" |
| DURATION | Time periods | "30 days" |

## API Usage

### Start API Server
```bash
python api_server.py
```

### Extract Entities
```bash
curl -X POST http://localhost:5001/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "This agreement between ACME Corp and John Doe..."}'
```

## Configuration

### Environment Variables
```bash
export DOCKER_CONTAINER_NAME=legal-ner-api
export API_PORT=5001
export MAX_TEXT_LENGTH=10000
```

### Model Settings
```python
# In train_spacy.py
config = {
    "dropout": 0.2,
    "batch_size": 32,
    "learn_rate": 0.001,
    "n_iter": 100
}
```

## Performance

- **Processing Speed:** ~1-2 seconds per page
- **Accuracy:** 85-95% (depending on document quality)
- **Memory Usage:** 2-4GB for training
- **Supported Formats:** PDF, TXT

## Troubleshooting

### Common Issues

1. **OCR Errors:**
   ```bash
   # Check poppler/tesseract installation
   docker exec legal-ner-api which pdftoppm
   docker exec legal-ner-api which tesseract
   ```

2. **API Connection:**
   ```bash
   # Check if container is running
   docker ps | grep legal-ner-api
   
   # Restart if needed
   docker restart legal-ner-api
   ```

3. **Memory Issues:**
   ```bash
   # Reduce batch size in training
   python train_spacy.py --batch-size 16
   ```

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=1
python clean_pdf_entities.py --debug document.pdf
```

## Advanced Features

### Custom Entity Types
```python
# Add new entity types in entity_definitions.md
NEW_ENTITY_TYPES = ["CONTRACT_TERM", "OBLIGATION"]
```

### Batch Processing
```bash
# Process multiple PDFs
python batch_process.py --input-dir data/raw pdfs/ --output-dir results/
```

### Model Fine-tuning
```bash
# Fine-tune existing model
python train_spacy.py \
  --base-model data/models/base_model \
  --train-data data/spacy/new_data.spacy
```

## Contributing

1. Fork repository
2. Create feature branch
3. Submit pull request



## Support

For issues:
1. Check troubleshooting section
2. Review logs in `logs/` directory
3. Create GitHub issue with details

---

**Quick Start:** Run `./setup.sh` for automated setup and testing.
    