# vector_store.py

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
import streamlit as st

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load the embedding model
        self.embedder = SentenceTransformer(model_name)
        self.index = None
        self.text_chunks = []

    def create_index(self, full_text: str):
        """
        Create FAISS index with progress tracking
        """
        progress_bar = st.progress(0, "Initializing...")
        
        try:
            # 1) Split text into chunks (25%)
            progress_bar.progress(0.1, "Splitting text into chunks...")
            splitter = RecursiveCharacterTextSplitter(
                # Try to split on these characters, in order
                separators=["\n\n", "\n", ".", "!", "?", " ", ""],
                chunk_size=500,  # slightly larger chunks for better context
                chunk_overlap=50,  # reduced overlap since chunks are more meaningful
                length_function=len,
            )
            chunks = splitter.split_text(full_text)
            self.text_chunks = chunks
            progress_bar.progress(0.25, "Text splitting complete.")

            # 2) Compute embeddings (50%)
            progress_bar.progress(0.3, "Computing embeddings...")
            embeddings = self.embedder.encode(
                chunks,
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32
            )
            progress_bar.progress(0.75, "Embeddings computed.")            
            # 3) Build FAISS index (25%)
            progress_bar.progress(0.8, "Building search index...")
            d = embeddings.shape[1]
            faiss.normalize_L2(embeddings)  # Normalize vectors for better similarity
            index = faiss.IndexFlatL2(d)
            index.add(embeddings)
            self.index = index
            
            # Done!
            progress_bar.progress(1.0, "Vector store ready!")
            
        except Exception as e:
            progress_bar.empty()
            raise e  # Re-raise to be caught by the app

    def retrieve(self, query: str, k: int = 3):
        """
        Given a query string, return the top-k most relevant text chunks.
        """
        if self.index is None:
            return []        # Embed the query and normalize
        q_emb = self.embedder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)  # Normalize query vector same as index vectors
        # Search FAISS
        distances, indices = self.index.search(q_emb, k)
        results = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])
        return results
