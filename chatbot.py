import os
import requests
import json
from vector_store import VectorStore
from dotenv import load_dotenv

# Load Groq API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

# 1) Initialize Vector Store
vs = VectorStore(model_name="all-MiniLM-L6-v2")

def build_vector_store_from_text(full_text: str):
    """
    Build FAISS index over the PDF's full text.
    Call this after you extract text from the PDF.
    """
    vs.create_index(full_text)

def answer_with_rag(question: str, top_k: int = 10, return_chunks: bool = False, stream: bool = False, chat_history=None):
    """
    1) Retrieve top_k relevant chunks via FAISS
    2) Concatenate chunks into context
    3) Use Groq's LLaMA3 to answer via streaming or normal
    4) Optionally include last 3 Q&A turns from chat_history for follow-up support
    """
    chunks = vs.retrieve(question, k=top_k * 4)
    if not chunks:
        return ("No relevant information found.", []) if return_chunks else "No relevant information found."

    # Combine context
    context = "\n".join(chunks)
    if len(context) > 6000:
        context = context[:6000]

    # Add last 2 user questions from chat_history if provided (no answers)
    history_str = ""
    if chat_history:
        # Only use last 2 user questions (not answers)
        last_turns = chat_history[-2:]
        for turn in last_turns:
            user_q = turn.get("user", "")
            if user_q:
                history_str += f"User: {user_q}\n"
        if history_str:
            history_str = f"Previous questions (last 2):\n" + history_str + "---\n"

    prompt = (
        "Answer the user's question using only the provided document context. "
        "Be clear, concise, and explain as if teaching a student. "
        "If the answer is not present, say so.\n"
        f"{history_str}"
        f"Context from the document:\n{context}\n"
        f"User's new question: {question}\n"
        f"Answer:"
    )

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
        "stream": stream
    }

    if stream:
        # STREAMING RESPONSE MODE
        def stream_generator():
            response = requests.post(GROQ_API_URL, headers=headers, json=data, stream=True)
            for line in response.iter_lines():
                if line and line.strip().startswith(b"data:"):
                    clean = line.decode().replace("data: ", "").strip()
                    if clean == "[DONE]":
                        break
                    try:
                        delta = json.loads(clean)["choices"][0]["delta"]
                        yield delta.get("content", "")
                    except Exception as e:
                        yield f"\n[Error parsing stream chunk: {e}]"
        return stream_generator()
    
    else:
        # NON-STREAMED (normal) RESPONSE MODE
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        try:
            resp_json = response.json()
        except Exception as e:
            return f"[Groq API error: Could not parse response] {response.text}"

        print("Groq API response:", resp_json)

        if response.status_code == 200:
            answer = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "[No content in response]").strip()

            # Flag suspicious content (like if Groq returned an API key or something wrong)
            if answer.startswith("gsk_") or len(answer) < 5:
                return f"[Groq API suspicious response] {resp_json}"
        else:
            return f"[Groq API error {response.status_code}] {response.text}"

        return (answer, chunks) if return_chunks else answer
