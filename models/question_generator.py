from models.rag_engine import rag_engine
from utils.ai_helper import generate_with_gemini

def generate_questions(text):
    rag_engine.add_documents(text)
    context = " ".join(rag_engine.retrieve(text))
    combined_context = f"{context}\n\nBased on this content, generate educational questions."
    questions = generate_with_gemini(combined_context)
    return questions
