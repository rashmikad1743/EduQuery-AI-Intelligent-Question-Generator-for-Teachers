# ...existing code...
import os
import numpy as np

try:
    import faiss
    _HAS_FAISS = True
except Exception:
    _HAS_FAISS = False

class RAGEngine:
    def __init__(self, path: str = None, embed_model_name: str = "all-MiniLM-L6-v2"):
        """
        Lazy-loading RAG engine. Will attempt to use SentenceTransformer when needed.
        If that fails, falls back to a TF-IDF retriever (no heavy torch deps).
        """
        self.path = path
        self.embed_model_name = embed_model_name
        self.embed_model = None
        self.use_transformer = False

        # storage
        self.texts = []            # list of text chunks (strings)
        self.metadatas = []        # optional metadata per chunk
        self.embeddings = None     # numpy array of embeddings (transformer) or TF-IDF dense matrix
        self.index = None          # faiss index when available for transformer embeddings
        # TF-IDF fallback objects
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None

    def _ensure_transformer(self):
        """Attempt to import and instantiate SentenceTransformer (lazy)."""
        if self.embed_model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            # force CPU to avoid GPU/meta device moves
            self.embed_model = SentenceTransformer(self.embed_model_name, device="cpu")
            self.use_transformer = True
        except Exception:
            # transformer not available or failed -> use TF-IDF fallback
            self.embed_model = None
            self.use_transformer = False

    def add_documents(self, docs):
        """
        docs: either a single string, list of strings, or list of tuples (text, metadata)
        """
        if isinstance(docs, str):
            self.texts.append(docs)
            self.metadatas.append({})
            return

        # list handling
        for item in docs:
            if isinstance(item, tuple) or isinstance(item, list):
                text = item[0]
                meta = item[1] if len(item) > 1 else {}
            else:
                text = str(item)
                meta = {}
            self.texts.append(text)
            self.metadatas.append(meta)

        # Invalidate previous index/embeddings
        self.embeddings = None
        self.index = None
        self._tfidf_matrix = None
        self._tfidf_vectorizer = None

    def build_index(self):
        """Build embeddings + index. Prefer transformer; fallback to TF-IDF."""
        if not self.texts:
            return

        # Try transformer path first
        self._ensure_transformer()
        if self.use_transformer and self.embed_model is not None:
            try:
                embs = self.embed_model.encode(self.texts, convert_to_numpy=True, show_progress_bar=False)
                # normalize for inner-product cosine similarity with faiss (if used)
                norms = np.linalg.norm(embs, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                embs = embs / norms

                self.embeddings = embs
                if _HAS_FAISS:
                    d = embs.shape[1]
                    self.index = faiss.IndexFlatIP(d)
                    self.index.add(embs)
                else:
                    self.index = None
                return
            except Exception:
                # fall back to TF-IDF below
                self.embed_model = None
                self.use_transformer = False

        # TF-IDF fallback
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vec = TfidfVectorizer(max_features=20000)
            matrix = vec.fit_transform(self.texts)
            # convert to dense float32 for simple computations (ok for small corpora)
            self._tfidf_vectorizer = vec
            self._tfidf_matrix = matrix.astype(np.float32)
            self.embeddings = None
            self.index = None
        except Exception:
            # last-resort: store no embeddings
            self._tfidf_vectorizer = None
            self._tfidf_matrix = None
            self.embeddings = None
            self.index = None

    def has_index(self):
        return (self.index is not None) or (self.embeddings is not None) or (self._tfidf_matrix is not None)

    def retrieve(self, query: str, top_k: int = 3):
        """Return list of metadata dicts (with 'text_snippet' and original text) for top_k results."""
        if not self.texts:
            return []

        # Ensure index built
        if not self.has_index():
            self.build_index()

        # Transformer retrieval
        if self.use_transformer and self.embeddings is not None:
            try:
                q_emb = self.embed_model.encode([query], convert_to_numpy=True)
                # normalize
                q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-12)
                if self.index is not None:
                    D, I = self.index.search(q_emb, top_k)
                    indices = [int(i) for i in I[0] if i >= 0]
                else:
                    # brute-force cosine similarity
                    sims = (self.embeddings @ q_emb.T).squeeze()
                    indices = list(np.argsort(-sims)[:top_k])
                results = []
                for idx in indices:
                    results.append({
                        "chunk_id": idx,
                        "text_snippet": (self.texts[idx][:400] + ("..." if len(self.texts[idx])>400 else "")),
                        "text": self.texts[idx],
                        **(self.metadatas[idx] if idx < len(self.metadatas) else {})
                    })
                return results
            except Exception:
                pass  # fall through to TF-IDF fallback

        # TF-IDF retrieval fallback
        if self._tfidf_vectorizer is not None and self._tfidf_matrix is not None:
            try:
                q_vec = self._tfidf_vectorizer.transform([query]).astype(np.float32)
                # cosine similarity = (A·B) / (||A||*||B||); using dense approach
                from sklearn.metrics.pairwise import linear_kernel
                sims = linear_kernel(q_vec, self._tfidf_matrix).flatten()
                indices = list(np.argsort(-sims)[:top_k])
                results = []
                for idx in indices:
                    results.append({
                        "chunk_id": idx,
                        "text_snippet": (self.texts[idx][:400] + ("..." if len(self.texts[idx])>400 else "")),
                        "text": self.texts[idx],
                        **(self.metadatas[idx] if idx < len(self.metadatas) else {})
                    })
                return results
            except Exception:
                pass

        # Last-resort: return first top_k texts
        results = []
        for idx in range(min(top_k, len(self.texts))):
            results.append({
                "chunk_id": idx,
                "text_snippet": (self.texts[idx][:400] + ("..." if len(self.texts[idx])>400 else "")),
                "text": self.texts[idx],
                **(self.metadatas[idx] if idx < len(self.metadatas) else {})
            })
        return results

    def get_all_text(self):
        return "\n\n".join(self.texts)

# create a default instance if module used directly
rag_engine = RAGEngine()
# ...existing code...