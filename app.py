# app.py

import streamlit as st
from pdf_reader import extract_text_from_pdf
from chatbot import build_vector_store_from_text, answer_with_rag

st.set_page_config(page_title="Chat with PDF (RAG)", page_icon="🤖")
st.title("📘 Chat with PDF (Vector Search + QA)")

# STEP 1: Upload PDF & Build Index
st.sidebar.header("📄 Upload PDF")
pdf_file = st.sidebar.file_uploader("Choose a PDF", type=["pdf"])

if pdf_file is None:
    st.info("👈 Upload a PDF in the sidebar to get started.")
    st.stop()

# Extract text and build the FAISS index once
if 'vector_store_built' not in st.session_state or st.session_state.get('last_pdf_filename') != getattr(pdf_file, 'name', None):
    with st.spinner("Extracting PDF text and building vector store..."):
        full_text = extract_text_from_pdf(pdf_file)
        build_vector_store_from_text(full_text)
    st.session_state['vector_store_built'] = True
    st.session_state['last_pdf_filename'] = getattr(pdf_file, 'name', None)
st.sidebar.success("Vector store ready! You can now ask questions.")

# STEP 2: Ask Questions
st.subheader("Ask a question about the PDF:")
question = st.text_input("Your question:", key="question_input", on_change=None)
ask_clicked = st.button("Ask", key="ask_button")

# Use session state to track the last answered question
if 'last_answered_question' not in st.session_state:
    st.session_state['last_answered_question'] = ''

# Trigger answer if Ask is clicked or Enter is pressed with a new question
trigger_answer = False
if ask_clicked and question:
    trigger_answer = True
elif question and question != st.session_state['last_answered_question'] and not ask_clicked:
    trigger_answer = True

if trigger_answer:
    with st.spinner("Searching for the answer..."):
        answer = answer_with_rag(question, top_k=3)
    st.markdown(f"**Answer:** {answer}")
    st.session_state['last_answered_question'] = question
