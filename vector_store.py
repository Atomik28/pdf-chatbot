from sentence_transformers import SentenceTransformer
from langchain.text_splitter import CharacterTextSplitter
import faiss
import numpy as np

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load a sentence-transformer model
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
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_text(full_text)
        self.text_chunks = chunks  # store for retrieval

        # 2) Compute embeddings (batch encode)
        embeddings = self.embedder.encode(chunks, convert_to_numpy=True, show_progress_bar=True)

        # 3) Build a FAISS index (flat L2)
        d = embeddings.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(embeddings)
        self.index = index

    def retrieve(self, query: str, k: int = 3):
        """
        Given a query string, return the top‐k text chunks.
        """
        # 1) Embed the query
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        # 2) Search FAISS
        distances, indices = self.index.search(q_emb, k)
        # 3) Fetch the chunks
        results = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])
        return results
