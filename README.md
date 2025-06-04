# Chat with PDF AI

A simple Gen AI app that allows you to chat with any PDF. Built with:

- **HuggingFace API** for embeddings & Q&A  
- **LangChain** for chaining the retrieval + generation workflow  
- **FAISS** as a vector store for fast semantic search  
- **Streamlit** for a quick web UI  

## How It Works

1. **Upload a PDF**: The app extracts all text from the PDF.  
2. **Create Vector Store**: Text is split into chunks and converted to embeddings. These are stored in a FAISS index.  
3. **Ask a Question**: User enters a query in the chat input.  
4. **Retrieve**: The app embeds the query, searches FAISS for the most similar PDF chunks.  
5. **Generate**: The relevant chunks + query are sent to GPT-3.5, which returns an answer.  
6. **Display**: The answer (and optionally the source chunks) are shown in the Streamlit UI.

## File Structure

chat-with-pdf-ai/
│
├── app.py # Streamlit UI
├── pdf_reader.py # PDF text extraction
├── vector_store.py # FAISS vector store creation
├── chatbot.py # RAG chain & query function
├── requirements.txt # Dependencies
└── README.md # This file