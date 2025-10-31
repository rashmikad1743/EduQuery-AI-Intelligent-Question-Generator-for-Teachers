# 🧠 EduQuery — AI Question Generator for Teachers

**EduQuery** is an AI-powered assistant that automatically generates **curriculum-aligned questions** (MCQs, short answer, and descriptive) from educational materials like PDFs, lecture notes, or pasted text.

It uses a **Retrieval-Augmented Generation (RAG)** pipeline integrated with **Google Gemini LLM** to create high-quality, context-aware questions for teachers.

---

## 🚀 Features

* 📚 Upload PDF or paste text content
* 🧩 Retrieve document context using **Vectorstore (RAG)**
* 🤖 Generate **MCQs**, **Short Answer**, and **Descriptive** questions using **Gemini API**
* 💾 Save generated questions in **SQLite database**
* 🌐 User-friendly **Flask web app** (optional Streamlit frontend)
* 🔄 Persistent **vectorstore.pkl** for faster reloading

---

## 🏗️ Project Structure

```
EduQuery/
│
├── app.py                        # Main Flask application
│
├── models/                       # Core backend logic
│   ├── rag_engine.py             # RAG engine for document retrieval
│   ├── question_generator.py     # Combines retrieval and LLM question generation
│   ├── database.py               # Handles database models and operations
│   └── __init__.py
│
├── templates/                    # Frontend (HTML using Jinja2)
│   ├── base.html                 # Common layout
│   ├── index.html                # Homepage
│   ├── generate.html             # Upload & generate page
│   ├── results.html              # Display generated questions
│   └── history.html              # Shows saved question sets
│
├── utils/                        # Helper functions and utilities
│   ├── ai_helper.py              # Gemini API wrapper & prompt builder
│   ├── file_loader.py            # PDF/Text file loader
│   └── validators.py             # Input validation utilities
│
├── data/                         # SQLite DB and saved artifacts
│   └── questions.db
│
├── vectorstore.pkl               # Persisted RAG vectorstore (auto-generated)
│
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not committed)
└── README.md                     # Project documentation
```

---

## ⚙️ Requirements

* **Python:** 3.11+
* **OS:** Windows (PowerShell commands used)
* **LLM:** Gemini API key (Google Generative AI)
* **Hardware:** CPU (GPU optional)

---

## 🧩 Setup (Windows)

### 1️⃣ Create and activate virtual environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2️⃣ Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Create `.env` file in project root

```env
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
VECTORSTORE_PATH=./vectorstore.pkl
```

**Note:**

* `SECRET_KEY` → Flask session encryption key
* `GEMINI_API_KEY` → Used in `utils/ai_helper.py`
* `VECTORSTORE_PATH` → Path for saved embeddings

### 4️⃣ Ensure data directory exists

```powershell
mkdir data
```

---

## ▶️ Run the Application

### Flask App

```powershell
python app.py
```

Visit: **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

### Optional Streamlit Frontend

```powershell
streamlit run streamlit_app.py
```

---

## 🧠 How It Works

1. Upload a **PDF** or **paste content**.
2. Select question type (MCQ, Short, Descriptive) and number of questions.
3. The **RAG engine** retrieves the most relevant context.
4. The **Gemini LLM** generates context-based questions.
5. Questions are displayed and stored in the **SQLite database**.

---

## 🧰 Common Issues & Fixes

| Issue                            | Solution                                                      |
| -------------------------------- | ------------------------------------------------------------- |
| `ModuleNotFoundError: dotenv`    | Install: `pip install python-dotenv`                          |
| `SQLite: file is not a database` | Delete DB: `del data\questions.db`                            |
| Gemini model not found           | Run: `genai.list_models()` to find valid model name           |
| Import errors (NumPy/Torch)      | Use clean venv, run: `pip install "numpy<2"`                  |
| API import slow                  | Upgrade: `pip install --upgrade google-generativeai protobuf` |

---

## 🧪 Development Notes

* **RAG engine** retrieves top-K chunks using semantic embeddings (SentenceTransformers).
* **AI Helper** builds structured prompts for Gemini LLM.
* Generated sets stored in `QuestionSet` and `Question` tables (Flask-SQLAlchemy).
* Retrieval can be tuned by modifying chunk size or embedding models.


## 🧾 Contribution

1. Fork the repository.
2. Create a new branch: `feature/your-feature-name`
3. Add new features or improvements.
4. Commit and push changes.
5. Submit a pull request with a clear description.



✅ **Developed by:** *Rashmika Rohit*
🎓 *L.D. College of Engineering | AI & ML Engineering*
🌐 GitHub: [@rashmikad1743](https://github.com/rashmikad1743)
