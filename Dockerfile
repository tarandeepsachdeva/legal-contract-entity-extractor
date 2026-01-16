FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy and download model
RUN pip install spacy==3.7.2
RUN python -m spacy download en_core_web_sm

# Install additional PDF processing libraries
RUN pip install PyMuPDF==1.23.8 pdf2image==1.16.3 pytesseract==0.3.10

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/models

# Expose port
EXPOSE 5001

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=api.py
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run the application
CMD ["python", "api.py"]
