from transformers import pipeline
from vector_store import VectorStore

# Load extractive QA pipeline (DistilBERT-SQuAD)
qa_pipeline = pipeline(
    "question-answering",
    model="distilbert-base-cased-distilled-squad",
    tokenizer="distilbert-base-cased-distilled-squad"
)

# Initialize the VectorStore (embeds with all-MiniLM-L6-v2)
vs = VectorStore(model_name="all-MiniLM-L6-v2")

def build_vector_store_from_text(full_text: str):
    """
    Build FAISS index over the PDF text. Call this once after PDF upload.
    """
    vs.create_index(full_text)

def answer_with_rag(question: str, top_k: int = 3):
    """
    1) Retrieve top_k chunks via FAISS
    2) Run extractive QA on each chunk
    3) Return the highest‐confidence answer
    """
    # 1) Retrieve relevant chunks
    chunks = vs.retrieve(question, k=top_k)
    all_answers = []

    # 2) Run the QA pipeline over each chunk
    for chunk in chunks:
        result = qa_pipeline({
            "context": chunk,
            "question": question
        })
        # result contains 'score', 'answer'
        all_answers.append(result)

    # 3) Pick the best answer by score
    if not all_answers:
        return "No relevant information found."
    best = max(all_answers, key=lambda x: x["score"])
    return best["answer"]
