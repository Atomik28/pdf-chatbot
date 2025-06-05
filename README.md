# Chat with PDF AI (DocTalk)

A fast, student-friendly GenAI app to chat with any PDF using Retrieval-Augmented Generation (RAG). Built with:

- **Local Sentence Transformers** for embeddings (all-MiniLM-L6-v2)
- **FAISS** for fast semantic search
- **Streamlit** for a modern, chat-style web UI
- **Groq API (Llama3-70B)** for answer generation

## How to Use This

1. **Clone the repository:**
   ```sh
   git clone <your-remote-repo-url>
   cd pdf-chatbot
   ```
2. **Create a virtual environment (recommended):**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # Or: source .venv/bin/activate  # On Mac/Linux
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Get a Groq API key:**
   - Go to [Groq Cloud](https://console.groq.com/keys) and sign up or log in.
   - Create a new API key and copy it.
5. **Create a `.env` file in the project root:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
6. **Run the app:**
   ```sh
   streamlit run app.py
   ```
7. **Open your browser:**
   - Go to the local URL shown in the terminal (usually http://localhost:8501)
   - Upload a PDF and start chatting!

## How It Works

1. **Upload a PDF**: The app extracts all text from your PDF.
2. **Create Vector Store**: Text is split into overlapping chunks and embedded locally. Chunks are stored in a FAISS index for fast retrieval.
3. **Ask Questions**: Type questions in the chat interface. Each question is answered in a conversational, student-friendly way.
4. **Retrieve**: The app embeds your query, searches FAISS for the most relevant PDF chunks.
5. **Generate**: The retrieved context and your question are sent to Groq's Llama3-70B for a detailed, easy-to-understand answer.
6. **Display**: Answers appear in a chat window. You can export your chat or clear it at any time.

## Features
- Modern chat UI with persistent Q&A history (per session)
- Handles up to 50 questions per session
- Download your chat as a text file
- Clear chat and reset with a single click
- Robust PDF extraction and fast, local retrieval
- No OpenAI/HuggingFace API required for embeddings (runs locally)

## File Structure

```
chat-with-pdf-ai/
│
├── app.py            # Streamlit UI and chat logic
├── pdf_reader.py     # PDF text extraction
├── vector_store.py   # FAISS vector store and embedding
├── chatbot.py        # RAG pipeline and Groq API integration
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Requirements
- Python 3.9+
- See `requirements.txt` for all dependencies

## Notes
- All processing is local except for answer generation (Groq API required; set `GROQ_API_KEY` in your `.env` file)
- For best results, use clear textbook-style PDFs

---

Made with ❤️ for students. Powered by Llama3-70B via Groq.