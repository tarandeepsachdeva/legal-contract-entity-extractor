from pdf2image import convert_from_path
import pytesseract

def scannedPdf_textExtraction(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text
