import streamlit as st
from pdf_reader import extract_text_from_pdf
from chatbot import build_vector_store_from_text, answer_with_rag
from st_ui import configure_page, render_sidebar_header

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
st.sidebar.header("📄 Upload PDF")
pdf_file = st.sidebar.file_uploader("Choose a PDF", type=["pdf"])

if pdf_file is None:
    st.session_state.clear()
    st.info("👈 Upload a PDF in the sidebar to get started.")
    st.stop()

if (
    "vector_store_built" not in st.session_state
    or st.session_state.get("last_pdf_filename") != getattr(pdf_file, "name", None)
):
    with st.spinner("Extracting PDF text and building vector store..."):
        full_text = extract_text_from_pdf(pdf_file)
        build_vector_store_from_text(full_text)
    st.session_state["vector_store_built"] = True
    st.session_state["last_pdf_filename"] = getattr(pdf_file, "name", None)

st.sidebar.success("✅ Vector store ready! You can now ask questions.")

# ---------------------------------------
# STEP 2: Render Chat History (smartly)
# ---------------------------------------
st.subheader("Chat")

# Show all completed messages
for turn in st.session_state.chat_history[:-1]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        st.markdown(turn["bot"])

# Check and handle the latest message if it's still being generated
if st.session_state.chat_history:
    last_turn = st.session_state.chat_history[-1]
    with st.chat_message("user"):
        st.markdown(last_turn["user"])

    if last_turn["bot"]:
        with st.chat_message("assistant"):
            st.markdown(last_turn["bot"])
    else:
        full_answer = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Searching for the answer…"):
                for chunk in answer_with_rag(last_turn["user"], top_k=3, stream=True):
                    full_answer += chunk
                    placeholder.markdown(full_answer)
        st.session_state.chat_history[-1]["bot"] = full_answer

# ---------------------------------
# STEP 3: New Question Input (limit)
# ---------------------------------

num_asked = len(st.session_state.chat_history)
if num_asked < 50:
    user_question = st.chat_input("Type your question here and press Enter…")
else:
    user_question = None
    st.info("🛑 You have reached the 50-question limit for this chat. Refresh the page or click “Clear Chat” to start over.")

if user_question:
    st.session_state.chat_history.append({"user": user_question, "bot": ""})
    st.rerun()

# --------------------------------------------
# STEP 4: Show question‐count & export/clear
# --------------------------------------------
if num_asked > 0:
    st.sidebar.markdown(f"**Questions used:** {num_asked} / 50")

    def _export_chat_as_text(chat_list):
        lines = []
        for idx, turn in enumerate(chat_list, start=1):
            lines.append(f"Q{idx}: {turn['user']}")
            lines.append(f"A{idx}: {turn['bot']}")
            lines.append("")
        return "\n".join(lines)

    export_text = _export_chat_as_text(st.session_state.chat_history)
    st.sidebar.download_button(
        label="📥 Download Chat",
        data=export_text,
        file_name="chat_history.txt",
        mime="text/plain"
    )

    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
