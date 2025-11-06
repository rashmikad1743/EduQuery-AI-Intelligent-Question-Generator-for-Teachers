# 🧠 EduQuery — AI Question Generator for Teachers

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

**An AI-powered question generation assistant built for teachers and educators.**

</div>

---

## 📖 Overview

**EduQuery** is an AI-powered assistant that automatically generates **curriculum-aligned questions** — including **MCQs**, **short answers**, and **descriptive questions** — from educational materials like PDFs, lecture notes, or pasted text.

It uses a **Retrieval-Augmented Generation (RAG)** pipeline integrated with **Google Gemini LLM** to generate high-quality, context-aware questions and store them in a local database for reuse.

---

## 🚀 Features

| Feature | Description |
|----------|-------------|
| 📚 **Upload or Paste Content** | Upload PDFs or enter text directly in the app |
| 🧩 **Retrieval-Augmented Generation** | Uses vector embeddings to understand content |
| 🤖 **AI-Powered Question Generation** | Generates MCQs, short, and descriptive questions |
| 💾 **Persistent Storage** | Saves generated questions in SQLite database |
| ⚡ **Vectorstore Caching** | Reuses embeddings for faster reloads |
| 🧠 **Gemini LLM Integration** | Ensures contextually accurate question creation |
| 🌐 **Interactive Frontend** | Built with Streamlit and Flask (optional) |

---


---


## ⚙️ Requirements

| Requirement | Version |
|--------------|----------|
| 🐍 **Python** | 3.11+ |
| 💻 **OS** | Windows / macOS / Linux |
| 🤖 **LLM** | Google Gemini API |
| 🧠 **Frameworks** | Streamlit / Flask (optional) |
| 🧮 **Database** | SQLite |

---

## 🧩 Setup (Windows Example)

### 1️⃣ Create and Activate Virtual Environment

python -m venv venv
.\venv\Scripts\activate
2️⃣ Install Dependencies
bash
Copy code
pip install --upgrade pip
pip install -r requirements.txt
3️⃣ Create .env File
Create a .env file in your project root:

env
Copy code
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
VECTORSTORE_PATH=./vectorstore.pkl
Notes:

SECRET_KEY → Flask session encryption key

GEMINI_API_KEY → Used by Gemini LLM for question generation

VECTORSTORE_PATH → Path to your saved vector embeddings

4️⃣ Ensure Data Directory Exists
bash
Copy code
mkdir data
▶️ Running the Application
🧠 Flask Backend
bash
Copy code
python app.py
Then open your browser and visit:
👉 http://127.0.0.1:5000/

🌐 Streamlit Frontend (Optional)
bash
Copy code
streamlit run streamlit_app.py
The app will open automatically at:
👉 http://localhost:8501/ 🎉

🧠 How It Works
Upload a PDF or paste your text content.

Select question type (MCQ / Short / Descriptive).

RAG Engine retrieves relevant text chunks using embeddings.

Gemini LLM generates accurate, curriculum-based questions.

Results are displayed and stored in the local SQLite database.

🧰 Common Issues & Fixes
Issue	Solution
ModuleNotFoundError: dotenv	Run pip install python-dotenv
SQLite: file is not a database	Delete the old DB → del database\questions.db
Gemini model not found	Run genai.list_models() to check model name
ImportError: numpy or torch	Use compatible versions → pip install "numpy<2"
API import slow	Upgrade packages → pip install --upgrade google-generativeai protobuf

🧪 Technical Details
RAG Engine uses semantic embeddings (SentenceTransformers) to retrieve top-K document chunks.

Gemini LLM processes the retrieved context and generates structured question sets.

SQLite Database stores generated question sets for later use.

Performance Optimization via caching vectorstore (vectorstore.pkl) for fast reloads.

Flexible Frontend using Streamlit for educators to easily interact with AI.

🧾 Contribution Guide
Fork the repository.

Create a new branch:

bash
Copy code
git checkout -b feature/your-feature-name
Make your changes and commit them:

bash
Copy code
git commit -m "Add new feature"
Push to your branch:

bash
Copy code
git push origin feature/your-feature-name
Submit a Pull Request with a clear explanation.

👩‍💻 Author
Rashmika Rohit
🎓 Artificial Intelligence & Machine Learning Engineer
🏛️ L.D. College of Engineering

📧 rashmikad1743@gmail.com
💻 GitHub
🔗 LinkedIn

📜 License
This project is licensed under the MIT License.
See the LICENSE file for more details.

🙏 Acknowledgements
OMDb API — Movie dataset reference

Streamlit — Frontend framework

Google Gemini — AI model for question generation

Pandas — Data processing

FAISS — Vector similarity search

Shields.io — Badges for README styling

<div align="center">
⭐ If you found this project helpful, don’t forget to star the repository!
Made with ❤️ by Rashmika Rohit | Data & AI Engineer

</div> ```

