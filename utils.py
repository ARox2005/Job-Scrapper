import pdfplumber
from PIL import Image
import pytesseract

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()
    
def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using OCR (pytesseract)."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text.strip()