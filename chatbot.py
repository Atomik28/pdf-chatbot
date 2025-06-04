import os
import requests
from vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv()  
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

# 1) Initialize a VectorStore (use local embedding for now)
vs = VectorStore(model_name="all-MiniLM-L6-v2")

def build_vector_store_from_text(full_text: str):
    """
    Build FAISS index over the PDF's full text.
    Call this after you extract text from the PDF.
    """
    vs.create_index(full_text)

def answer_with_rag(question: str, top_k: int = 10, return_chunks: bool = False):
    """
    1) Retrieve top_k relevant chunks via FAISS (or all if short)
    2) Concatenate chunks and use Groq Llama3 for generation
    3) Return the generated answer (and optionally the source chunks)
    """
    # 1) Retrieve relevant chunks
    chunks = vs.retrieve(question, k=top_k * 4)  # retrieve even more chunks for better coverage
    if not chunks:
        return ("No relevant information found.", []) if return_chunks else "No relevant information found."

    # 2) Concatenate more chunks for context (increase max context length)
    max_context_length = 6000  # allow more context for the model
    context = "\n".join(chunks)
    if len(context) > max_context_length:
        context = context[:max_context_length]

    prompt = (
        "You are a helpful and knowledgeable assistant. Based only on the following excerpts from a textbook or document, answer the user's question as thoroughly and clearly as possible. "
        "If the answer is short enough, show the full answer in detail. If the answer is too long for the response, summarize long lists or explanations into concise bullet points, but do not omit any key information or steps. "
        "Explain in simple terms, as if teaching a student. Use clear language and examples if possible. "
        "If possible, quote or paraphrase relevant lines. If the answer is not present, say so.\n"
        f"Context:\n{context}\n"
        f"Question: {question}\n"
        f"Answer:"
    )

    # 3) Generate answer using Groq Llama3
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful and knowledgeable assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
        "top_p": 0.8,
        "stream": False
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    try:
        resp_json = response.json()
    except Exception as e:
        return f"[Groq API error: Could not parse response] {response.text}"
    if response.status_code == 200:
        # Debug: print the full response for inspection
        print("Groq API response:", resp_json)
        answer = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "[No content in response]").strip()
        # If the answer looks like an API key or token, show the full response
        if answer.startswith("gsk_") or len(answer) < 5:
            return f"[Groq API suspicious response] {resp_json}"
    else:
        return f"[Groq API error {response.status_code}] {response.text}"
    return (answer, chunks) if return_chunks else answer
