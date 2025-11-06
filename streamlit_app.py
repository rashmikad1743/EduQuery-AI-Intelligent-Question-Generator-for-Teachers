# streamlit_app.py
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from utils import pdf_to_text, chunk_text
from rag_engine import RAGEngine
from db import init_db, save_question, list_questions

# Load environment variables
load_dotenv()

# Read configuration from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "questions.db")
VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "vectorstore.pkl")

# Initialize database
init_db(DB_PATH)

# Streamlit setup
st.set_page_config(page_title="EduQuery — AI Question Generator", layout="wide")
st.title("🎓 EduQuery — AI Question Generator for Teachers")

# Sidebar options
st.sidebar.header("📁 Upload & Settings")
uploaded = st.sidebar.file_uploader("Upload PDF (or leave blank and paste text)", type=["pdf"])
text_input = st.sidebar.text_area("Or paste text here", height=200)
k = st.sidebar.slider("Retrieval top-K", 1, 10, 4)
mcq_count = st.sidebar.number_input("Number of MCQs", min_value=0, max_value=20, value=5)
short_count = st.sidebar.number_input("Short-answer questions", min_value=0, max_value=20, value=5)
desc_count = st.sidebar.number_input("Descriptive questions", min_value=0, max_value=10, value=3)

# Initialize RAG Engine
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine(path=VECTORSTORE_PATH)
rag = st.session_state.rag

# -------------------------------
# Document ingestion
# -------------------------------
st.header("📘 Step 1: Ingest Document")

doc_text = None
if uploaded is not None:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded.getbuffer())
    st.success("✅ PDF uploaded successfully.")
    doc_text = pdf_to_text("uploaded.pdf")
elif text_input.strip():
    doc_text = text_input

if doc_text and st.button("Ingest Document"):
    chunks = chunk_text(doc_text, chunk_size=800, overlap=150)
    docs = [(c, {"chunk_id": i, "text_snippet": c[:250]}) for i, c in enumerate(chunks)]
    rag.add_documents(docs)
    st.success(f"Ingested {len(docs)} chunks into the vectorstore.")

# -------------------------------
# Retrieve Context
# -------------------------------
st.markdown("---")
st.header("🔍 Step 2: Retrieve Context")
query = st.text_input("Enter topic or keyword (e.g., 'Photosynthesis')")

if st.button("Retrieve Context"):
    if not query.strip():
        st.error("Please enter a topic first.")
    else:
        results = rag.retrieve(query, top_k=k)
        if not results:
            st.warning("⚠️ Vectorstore is empty — please ingest a document first.")
        else:
            for i, r in enumerate(results):
                st.markdown(f"**Chunk {i+1}:** {r.get('text_snippet')}")

# -------------------------------
# Gemini API Call (Updated)
# -------------------------------
st.markdown("---")
st.header("🤖 Step 3: Generate Questions using Gemini API")

def call_gemini(prompt_text: str) -> str:
    """Call Google Gemini API using updated v1 endpoint."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [
            {"parts": [{"text": prompt_text}]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract Gemini response text
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"]
        return "⚠️ No text response found from Gemini API."
    except Exception as e:
        return f"❌ Error calling Gemini API: {e}"


# Generate button
if st.button("Generate Questions"):
    if not query.strip():
        st.error("Please enter a query/topic first.")
    else:
        contexts = rag.retrieve(query, top_k=k)
        combined_context = "\n\n".join([c.get("text_snippet", "") for c in contexts])
        prompt = (
            f"You are a question generator for teachers.\n\nContext:\n{combined_context}\n\n"
            f"Generate {mcq_count} multiple-choice questions (with 4 options and indicate the correct one), "
            f"{short_count} short-answer questions with answers, and "
            f"{desc_count} descriptive questions."
        )

        with st.spinner("⏳ Generating questions using Gemini..."):
            gen_text = call_gemini(prompt)

        st.subheader("✨ Generated Questions")
        st.code(gen_text)

        if st.button("💾 Save to Database"):
            save_question(
                source=query,
                question_type="Gemini_output",
                question_text=gen_text,
                choices="",
                answer="",
                metadata=json.dumps({"context_count": len(contexts)}),
                path=DB_PATH,
            )
            st.success("✅ Output saved successfully!")

# -------------------------------
# View Saved Questions
# -------------------------------
st.markdown("---")
st.header("🗂️ Step 4: View Saved Questions")

rows = list_questions(DB_PATH)
if rows:
    for r in rows[:10]:
        st.markdown(f"**{r['question_type']}** — *{r['source']}* ({r['created_at']})")
        st.write(r["question_text"][:800])
        st.markdown("---")
else:
    st.info("No saved questions yet. Generate and save to view here.")
