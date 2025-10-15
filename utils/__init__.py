from PyPDF2 import PdfReader
import io

def extract_text_from_pdf(file):
    reader = PdfReader(io.BytesIO(file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()
