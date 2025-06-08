import streamlit as st
import base64


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
    Export chat history (list of dicts with 'user' and 'bot') to a PDF and return bytes using ReportLab (full Unicode support).
    """
    from io import BytesIO
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib import colors
    import re

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontName = "Times-Roman"
    normal.fontSize = 12
    bold = ParagraphStyle(name="Bold", parent=normal, fontName="Times-Bold")
    code = ParagraphStyle(name="Code", parent=normal, fontName="Courier", fontSize=10, backColor=colors.whitesmoke, leftIndent=12)
    elements = []

    elements.append(Paragraph("<b>DocTalk Chat History</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    for idx, turn in enumerate(chat_history, start=1):
        elements.append(Paragraph(f"<b>Q{idx}:</b> {turn['user']}", bold))
        answer = turn["bot"]
        code_block_pattern = re.compile(r"```([\w\+\-]*)\n([\s\S]*?)```", re.MULTILINE)
        pos = 0
        for match in code_block_pattern.finditer(answer):
            start, end = match.span()
            if start > pos:
                md = answer[pos:start]
                if md.strip():
                    elements.append(Paragraph(md.strip().replace("\n", "<br/>"), normal))
            code_text = match.group(2)
            code_html = f'<font face="Courier">{code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")}</font>'
            elements.append(Paragraph(code_html, code))
            pos = end
        if pos < len(answer):
            md = answer[pos:]
            if md.strip():
                elements.append(Paragraph(md.strip().replace("\n", "<br/>"), normal))
        elements.append(Spacer(1, 8))
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
