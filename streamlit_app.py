"""
AetherMind Multimodal AI — Enterprise AI Operating System
Native Streamlit Cloud Runner for Full-Stack FastAPI + HTML5/JS AetherMind UI
"""

import os
import sys
import threading
import time
import uvicorn
import streamlit as st
import streamlit.components.v1 as components

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Page Configuration
st.set_page_config(
    page_title="AetherMind Multimodal AI — Enterprise AI OS",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Start FastAPI Uvicorn Server in a background thread
def run_fastapi_server():
    try:
        from app.main import app
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
    except Exception as e:
        print(f"FastAPI Server thread error: {e}")

@st.cache_resource
def start_backend():
    thread = threading.Thread(target=run_fastapi_server, daemon=True)
    thread.start()
    time.sleep(2.5)  # Allow backend to initialize database & routers
    return True

start_backend()

# Inject Fullscreen Reset & Streamlit Chrome Removal CSS
st.markdown("""
<style>
    /* Hide Streamlit Chrome & Headers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stHeader"] {visibility: hidden;}
    
    /* Remove padding around container */
    .block-container {
        padding: 0rem !important;
        margin: 0rem !important;
        max-width: 100vw !important;
        height: 100vh !important;
    }
    
    .element-container, div.stMarkdown, div.stHtml {
        width: 100% !important;
        height: 100% !important;
    }

    iframe {
        width: 100vw !important;
        height: 98vh !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Render original full-stack AetherMind Web Application
try:
    st.iframe("http://127.0.0.1:8000", height=950, scrolling=True)
except Exception:
    components.iframe("http://127.0.0.1:8000", height=950, scrolling=True)
