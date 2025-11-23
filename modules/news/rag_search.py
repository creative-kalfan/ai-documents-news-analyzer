import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(__file__)
CORPUS_DIR = os.path.join(BASE_DIR, "resources", "sample_corpus")
INDEX_PATH = os.path.join(BASE_DIR, "resources", "faiss_index.bin")


class Retriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self._load_or_build_index()

    def _load_or_build_index(self):
        docs = []
        paths = []

        for file in os.listdir(CORPUS_DIR):
            if file.endswith(".txt"):
                fp = os.path.join(CORPUS_DIR, file)
                with open(fp, "r", encoding="utf-8") as f:
                    docs.append(f.read())
                    paths.append(fp)

        if not docs:
            self.documents = []
            return

        self.documents = docs
        embeddings = self.model.encode(docs, convert_to_numpy=True)
        embeddings = embeddings.astype("float32")

        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        faiss.write_index(index, INDEX_PATH)
        self.index = index

    def query(self, text, top_k=5):
        if not self.index:
            return []

        q_emb = self.model.encode([text], convert_to_numpy=True).astype("float32")
        D, I = self.index.search(q_emb, top_k)

        results = []
        for score, idx in zip(D[0], I[0]):
            results.append({
                "score": float(score),
                "text": self.documents[idx]
            })

        return results
