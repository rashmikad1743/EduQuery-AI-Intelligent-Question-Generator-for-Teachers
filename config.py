import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'questions.db')
import os

# Path to store the vectorstore file
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "vectorstore.pkl")

# 👇 Replace this with your actual key (after regenerating)
GEMINI_API_KEY = "AIzaSyDtoz4VTSxarpEvbswL0BZ_PmdUm4SS1h8"
