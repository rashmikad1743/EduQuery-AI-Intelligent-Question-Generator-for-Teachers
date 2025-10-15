import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import VECTORSTORE_PATH

class RAGEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.documents = []
        self.embeddings = None
        self.load_vectorstore()

    def add_documents(self, text):
        chunks = [text[i:i+800] for i in range(0, len(text), 800)]
        self.documents.extend(chunks)
        self.embeddings = self.vectorizer.fit_transform(self.documents)
        self.save_vectorstore()

    def retrieve(self, query, top_k=3):
        if not self.documents:
            return []
        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.embeddings).flatten()
        top_indices = sims.argsort()[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]

    def save_vectorstore(self):
        data = {"documents": self.documents, "vectorizer": self.vectorizer}
        with open(VECTORSTORE_PATH, 'wb') as f:
            pickle.dump(data, f)

    def load_vectorstore(self):
        if os.path.exists(VECTORSTORE_PATH):
            with open(VECTORSTORE_PATH, 'rb') as f:
                data = pickle.load(f)
                self.documents = data.get("documents", [])
                self.vectorizer = data.get("vectorizer", TfidfVectorizer(stop_words='english'))


rag_engine = RAGEngine()
