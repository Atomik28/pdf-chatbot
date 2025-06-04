import streamlit as st
from pdf_reader import extract_text_from_pdf
from chatbot import build_vector_store_from_text, answer_with_rag

st.set_page_config(page_title="Chat with PDF (RAG)", page_icon="🤖")
st.title("📘 Chat with PDF (Vector Search + QA)")

# ---- Upload PDF / Build Index ----
st.sidebar.header("📄 Upload PDF")
pdf_file = st.sidebar.file_uploader("Choose a PDF", type=["pdf"])
if pdf_file is not None:
    with st.spinner("Extracting text and building vector store..."):
        full_text = extract_text_from_pdf(pdf_file)
        build_vector_store_from_text(full_text)
    st.sidebar.success("Vector store ready! You can now ask questions.")
else:
    st.info("👈 Upload a PDF in the sidebar to get started.")
    st.stop()

# ---- Query Section ----
st.subheader("Ask a question about the PDF:")
question = st.text_input("Your question:")
if st.button("Get Answer") and question:
    with st.spinner("Searching..."):
        answer = answer_with_rag(question, top_k=3)
    st.markdown(f"**Answer:** {answer}")
