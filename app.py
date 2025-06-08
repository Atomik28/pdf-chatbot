import streamlit as st
from pdf_reader import extract_text_from_file, extract_text_from_files, PDFProcessError
from chatbot import build_vector_store_from_text, answer_with_rag
from st_ui import configure_page, render_sidebar_header, render_about_section, export_chat_history_to_pdf
import re

configure_page()
render_sidebar_header("assets/logo.png") 

# -------------------------------
# STEP 0: Initialize chat history
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Hide header/subheader if chat has started
show_headers = len(st.session_state.chat_history) == 0 and "bot" not in st.session_state.chat_history[-1] if st.session_state.chat_history else True
if len(st.session_state.chat_history) == 0:
    st.title("📘 DocTalk (based on LLAMA-3)")
    st.subheader("Ask a question about the PDF:")

# ---------------------------------------
# STEP 1: Upload PDF & Build Vector Store
# ---------------------------------------
st.sidebar.header("📄 Upload PDF or DOCX (multiple, max 50MB total)")
uploaded_files = st.sidebar.file_uploader(
    "Choose PDF or DOCX files",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="You can upload multiple files, but the total size must be under 50MB."
)

if not uploaded_files:
    st.session_state.clear()
    st.info("👈 Upload one or more PDF/DOCX files in the sidebar to get started.")
    st.stop()

# Enforce total size limit (50MB)
total_size = sum(getattr(f, 'size', 0) for f in uploaded_files)
if total_size > 50 * 1024 * 1024:
    st.error(f"⚠️ Total upload size is {total_size/1024/1024:.2f} MB. Please keep all files under 50MB combined.")
    st.session_state.clear()
    st.stop()

# Build a unique key for the current set of files (filenames + sizes)
file_key = tuple((getattr(f, 'name', None), getattr(f, 'size', 0)) for f in uploaded_files)

if (
    "vector_store_built" not in st.session_state
    or st.session_state.get("last_file_key") != file_key
):
    try:
        with st.spinner("Processing your files..."):
            full_text = extract_text_from_files(uploaded_files)
        if full_text:
            build_vector_store_from_text(full_text)
            st.session_state["vector_store_built"] = True
            st.session_state["last_file_key"] = file_key
            st.sidebar.success("✅ Vector store ready! You can now ask questions.")
    except PDFProcessError as e:
        st.error(f"⚠️ {str(e)}")
        st.session_state.clear()
        st.stop()
    except Exception as e:
        st.error("⚠️ An unexpected error occurred while processing the files. Please try again with different files.")
        st.session_state.clear()
        st.stop()

# ---------------------------------------
# STEP 2: Render Chat History (smartly)
# ---------------------------------------
st.subheader("Chat")

def render_markdown_with_codeblocks(text):
    """
    Render markdown text with code blocks using st.code for code and st.markdown for other text.
    This ensures the copy button works for full code blocks.
    """
    code_block_pattern = re.compile(r"```([\w\+\-]*)\n([\s\S]*?)```", re.MULTILINE)
    pos = 0
    for match in code_block_pattern.finditer(text):
        start, end = match.span()
        # Render any markdown before the code block
        if start > pos:
            md = text[pos:start]
            if md.strip():
                st.markdown(md)
        lang = match.group(1) or None
        code = match.group(2)
        st.code(code, language=lang)
        pos = end
    # Render any remaining markdown after the last code block
    if pos < len(text):
        md = text[pos:]
        if md.strip():
            st.markdown(md)

# Show all completed messages
for turn in st.session_state.chat_history[:-1]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        render_markdown_with_codeblocks(turn["bot"])

# Check and handle the latest message if it's still being generated
if st.session_state.chat_history:
    last_turn = st.session_state.chat_history[-1]
    with st.chat_message("user"):
        st.markdown(last_turn["user"])

    if last_turn["bot"]:
        with st.chat_message("assistant"):
            render_markdown_with_codeblocks(last_turn["bot"])
    else:
        full_answer = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Searching for the answer…"):
                for chunk in answer_with_rag(last_turn["user"], top_k=3, stream=True, chat_history=st.session_state.chat_history[:-1]):
                    full_answer += chunk
                    placeholder.markdown(full_answer)
        st.session_state.chat_history[-1]["bot"] = full_answer

# ---------------------------------
# STEP 3: New Question Input (limit)
# ---------------------------------
MAX_QUESTION_LENGTH = 500
num_asked = len(st.session_state.chat_history)

if num_asked < 50:
    user_question = st.chat_input("Type your question here and press Enter… (max 500 characters)")
    
    # Show character count if user is typing
    if user_question:
        current_length = len(user_question)
        if current_length > MAX_QUESTION_LENGTH:
            st.warning(f"⚠️ Your question is {current_length}/{MAX_QUESTION_LENGTH} characters. Please make it shorter.")
            st.stop()
        elif current_length > MAX_QUESTION_LENGTH * 0.8:  # Show counter when nearing limit
            st.info(f"ℹ️ Character count: {current_length}/{MAX_QUESTION_LENGTH}")
else:
    user_question = None
    st.info("🛑 You have reached the 50-question limit for this chat. 'Download' the chat and click “Clear Chat” to start over.")

if user_question:
    # Immediately show the user's question
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Add a small delay for better UX
    import time
    time.sleep(0.1)
    
    # Stream the answer in a new assistant message
    full_answer = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("Searching for the answer..."):
            for chunk in answer_with_rag(user_question, top_k=3, stream=True, chat_history=st.session_state.chat_history):
                full_answer += chunk
                # Use the custom renderer for streaming as well
                placeholder.markdown(full_answer)
    # Only after we have the complete answer, add both to history
    st.session_state.chat_history.append({
        "user": user_question,
        "bot": full_answer
    })

# --------------------------------------------
# STEP 4: Show question‐count & export/clear
# --------------------------------------------
if len(st.session_state.chat_history) > 0:
    # Count completed QA pairs (where both question and answer exist)
    num_questions = len([turn for turn in st.session_state.chat_history if turn.get("bot")])
    st.sidebar.markdown(f"**Questions used:** {num_questions} / 50")

    # PDF download button
    pdf_bytes = export_chat_history_to_pdf(st.session_state.chat_history)
    st.sidebar.download_button(
        label="📄 Download Chat (PDF)",
        data=pdf_bytes,
        file_name="chat_history.pdf",
        mime="application/pdf"
    )
    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# --------------------------------------------
# Render About section at the very bottom of sidebar when there is chat history
render_about_section()