# utils.py
from typing import List
from PyPDF2 import PdfReader


def pdf_to_text(path: str) -> str:
    """
    Extracts text from a PDF file and returns it as a single string.
    Handles unreadable pages gracefully.
    """
    try:
        reader = PdfReader(path)
        texts = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
                texts.append(text)
            except Exception as e:
                print(f"[WARN] Could not extract text from a page: {e}")
                continue
        return "\n".join(texts)
    except Exception as e:
        print(f"[ERROR] Failed to read PDF file '{path}': {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits a long text into overlapping chunks for vector embedding.
    """
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks
