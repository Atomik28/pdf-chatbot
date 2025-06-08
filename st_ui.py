import streamlit as st
import base64
from fpdf import FPDF
import tempfile

def render_about_section():
    """Renders the About section in the sidebar."""
    # Add spacing to push the about section to the bottom
    st.sidebar.markdown("<br>" * 2, unsafe_allow_html=True)
    
    about_expander = st.sidebar.expander("ℹ️ About", expanded=False)
    with about_expander:
        st.markdown("""
        ### 📘 DocTalk
        
        A smart PDF chatbot that lets you have natural conversations about your documents.
        
        #### How it works:
        1. Upload a PDF
        2. The app processes it using:
           - Text extraction (PyPDF2)
           - Text chunking and embeddings (LangChain)
           - Vector similarity (FAISS)
           - LLAMA language model
        3. Ask questions and get contextual answers!
        
        #### Features:
        - 📝 Smart text extraction
        - 🔍 Semantic search
        - 💬 Natural conversation
        - ⬇️ Export chat history
        - 🎯 Context-aware responses
        
        #### Made with:
        - Streamlit
        - LangChain
        - FAISS
        - LLAMA
        - PyPDF2
        
        #### Created by:
        [Prashant](https://github.com/Atomik28/pdf-chatbot)  
        
        ---
        """)

def get_base64_img(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def render_sidebar_header(logo_path="assets/logo.png", title="DocTALK"):
    icon_base64 = get_base64_img(logo_path)

    with st.sidebar:
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
                margin-top: 0px;
                padding-top: 0px;
                justify-content: flex-start;  /* Align left */
            ">
                <img src="{icon_base64}" width="30" height="30"/>
                <h3 style="margin: 0;">{title}</h3>
            </div>
            <hr style="margin-top: 5px; margin-bottom: 10px;" />
            """,
            unsafe_allow_html=True
        )



def configure_page():
    st.set_page_config(
        page_title="DocTALK",
        page_icon="assets/favicon.ico",  # This is still used for the browser tab
        layout="wide",
        initial_sidebar_state="expanded"
    )

def export_chat_history_to_pdf(chat_history, file_name="chat_history.pdf"):
    """
    Export chat history (list of dicts with 'user' and 'bot') to a PDF and return bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.set_title("DocTalk Chat History")
    pdf.cell(0, 10, "DocTalk Chat History", ln=True, align="C")
    pdf.ln(5)
    for idx, turn in enumerate(chat_history, start=1):
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(0, 8, f"Q{idx}: {turn['user']}", align="L")
        pdf.set_font("Arial", style="", size=12)
        # Render code blocks in bot answer as monospace, rest as normal
        answer = turn["bot"]
        import re
        code_block_pattern = re.compile(r"```([\w\+\-]*)\n([\s\S]*?)```", re.MULTILINE)
        pos = 0
        for match in code_block_pattern.finditer(answer):
            start, end = match.span()
            if start > pos:
                md = answer[pos:start]
                if md.strip():
                    pdf.multi_cell(0, 8, md.strip(), align="L")
            code = match.group(2)
            pdf.set_font("Courier", size=10)
            pdf.set_fill_color(240, 240, 240)
            for line in code.splitlines():
                pdf.cell(0, 6, line, ln=True, align="L", fill=True)
            pdf.set_font("Arial", size=12)
            pdf.set_fill_color(255, 255, 255)
            pos = end
        if pos < len(answer):
            md = answer[pos:]
            if md.strip():
                pdf.multi_cell(0, 8, md.strip(), align="L")
        pdf.ln(2)
    # Output to bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp.seek(0)
        pdf_bytes = tmp.read()
    return pdf_bytes
