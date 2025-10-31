🧠 EduQuery — AI Question Generator for Teachers

EduQuery is an AI-powered platform that automatically generates curriculum-aligned questions (MCQs, short answer, and descriptive) from educational materials such as PDFs, lecture notes, or plain text.

It leverages a Retrieval-Augmented Generation (RAG) pipeline integrated with a Large Language Model (Gemini) to create meaningful, context-aware question sets for teachers.

🚀 Features

📚 Upload PDF or paste educational text

🧩 Store and retrieve data context using Vectorstore (RAG)

🤖 Generate MCQs, Short Answer, and Descriptive questions using Gemini LLM

💾 Save generated question sets in a SQLite database

🌐 User-friendly Flask web interface (optional Streamlit integration)

🔄 Persistent vectorstore.pkl for fast reloading

🏗️ Project Structure
EduQuery/
│
├── app.py                        # Main Flask application
│
├── models/
│   ├── rag_engine.py             # RAG engine for document retrieval
│   ├── question_generator.py     # Handles retrieval + LLM question generation
│   ├── database.py               # Database helper for question storage
│   └── __init__.py
│
├── templates/                    # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── generate.html
│   ├── results.html
│   └── history.html
│
├── utils/
│   ├── ai_helper.py              # Gemini API wrapper and prompt builder
│   ├── file_loader.py            # PDF/Text file loader
│   └── validators.py             # Input and validation utilities
│
├── data/                         # SQLite DB and saved artifacts
│   └── questions.db
│
├── vectorstore.pkl               # Persisted RAG vectorstore
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
└── README.md                     # Documentation

⚙️ Requirements

Python: 3.11+

OS: Windows (commands below use PowerShell)

LLM: Gemini API key (Google Generative AI)

Hardware: CPU is sufficient (GPU optional)

🧩 Setup (Windows)

Create and activate a virtual environment

python -m venv venv
.\venv\Scripts\activate


Install dependencies

pip install --upgrade pip
pip install -r requirements.txt


Create .env file in the project root

SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
VECTORSTORE_PATH=./vectorstore.pkl


Explanation:

SECRET_KEY → Used by Flask for sessions

GEMINI_API_KEY → Used by utils/ai_helper.py

VECTORSTORE_PATH → Path for saving the vectorstore

Ensure data directory exists

mkdir data

▶️ Run the Application
Flask Web App
python app.py


Then open http://127.0.0.1:5000/
 in your browser.

Optional: Streamlit UI

If you have a Streamlit frontend:

streamlit run streamlit_app.py

🧠 How It Works

Upload a PDF or paste text on the Generate page.

Select question type (MCQ, Short, Descriptive) and quantity.

The RAG engine retrieves relevant document chunks.

The Gemini LLM generates context-based questions.

Questions are displayed and saved to the SQLite database for later use.

🧰 Common Issues & Fixes
Issue	Solution
ModuleNotFoundError: dotenv	pip install python-dotenv
SQLite: file is not a database	Delete corrupted DB: del data\questions.db
Gemini model error (404)	List models with:
genai.list_models() and use available names
Import errors with NumPy / Torch / Transformers	Use clean venv, install compatible versions:
pip install "numpy<2"
LLM API slow on first run	Allow time for imports; upgrade packages:
pip install --upgrade google-generativeai protobuf
🧪 Development Notes

The RAG engine retrieves top-K chunks based on semantic similarity (SentenceTransformers).

The AI Helper constructs structured prompts for Gemini to produce clear, formatted questions.

Generated papers are stored in QuestionSet and Question tables (Flask-SQLAlchemy).

You can improve retrieval by tuning chunk size or switching embedding models.

🧩 Example Prompt (Gemini)
prompt = f"""
Generate {num_questions} {question_type} questions from the given text.
Each question should be clear and relevant to the context.
Provide MCQ options (A, B, C, D) with the correct answer marked.

Text:
{text_content}
"""

💡 Contribution Guide

Fork the repository.

Create a new branch (feature/your-feature).

Add tests or improvements.

Submit a pull request with a clear description.
