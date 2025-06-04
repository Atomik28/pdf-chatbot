# vector_store.py

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter
import faiss
import numpy as np

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load the embedding model
        self.embedder = SentenceTransformer(model_name)
        self.index = None
        self.text_chunks = []

    def create_index(self, full_text: str):
        """
        1) Split full_text into overlapping chunks
        2) Compute embeddings
        3) Build a FAISS index
        """
        # 1) Chunk the text
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=300,  # even smaller chunk size for more granularity
            chunk_overlap=200  # high overlap to preserve context
        )
        chunks = splitter.split_text(full_text)
        self.text_chunks = chunks

        # 2) Compute embeddings for all chunks
        embeddings = self.embedder.encode(chunks, convert_to_numpy=True, show_progress_bar=False)

        # 3) Build a FAISS index (flat L2)
        d = embeddings.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        self.index = index

    def retrieve(self, query: str, k: int = 3):
        """
        Given a query string, return the top-k most relevant text chunks.
        """
        if self.index is None:
            return []

        # Embed the query
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        # Search FAISS
        distances, indices = self.index.search(q_emb, k)
        results = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])
        return results
