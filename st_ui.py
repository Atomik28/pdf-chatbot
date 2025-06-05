import streamlit as st
import base64

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
