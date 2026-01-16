import os
import glob

from ocr.pdf_text import pdf_textExtraction
from ocr.OCR_extractor import scannedPdf_textExtraction
from ocr.text_cleaning import clean_text


def process_pdf(pdf_path):
    """
    Decide whether the PDF is digital or scanned,
    extract text accordingly, then clean it.
    """

    
    if "scanned" in pdf_path.lower():
        text = scannedPdf_textExtraction(pdf_path)
        source_type = "scanned"
    else:
        text = pdf_textExtraction(pdf_path)
        source_type = "digital"

   
    if len(text.strip()) < 50:
        text = scannedPdf_textExtraction(pdf_path)
        source_type = "scanned"

   
    cleaned_text = clean_text(text)

    return cleaned_text, source_type


def save_extracted_text(text, output_path, source_type):
    """
    Save cleaned text to .txt file with metadata
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"SOURCE_TYPE: {source_type}\n\n")
        f.write(text)


def process_all_pdfs():
    """
    Batch process all PDFs from data/raw_pdfs
    and save outputs to data/extracted_text
    """

    base_data_path = "../data/raw pdfs"
    output_base_path = "../data/extracted_text"

    pdf_folders = ["Digital", "Scanned"]

    for folder in pdf_folders:
        input_folder = os.path.join(base_data_path, folder)
        output_folder = os.path.join(output_base_path, folder.lower())

        if not os.path.exists(input_folder):
            print(f"Folder not found: {input_folder}")
            continue

        pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))

        for pdf_path in pdf_files:
            print(f"Processing: {pdf_path}")

            try:
                extracted_text, source_type = process_pdf(pdf_path)

                pdf_name = os.path.basename(pdf_path)
                txt_name = os.path.splitext(pdf_name)[0] + ".txt"
                output_path = os.path.join(output_folder, txt_name)

                save_extracted_text(extracted_text, output_path, source_type)
                print(f"Saved → {output_path}")

            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")


if __name__ == "__main__":
    process_all_pdfs()
