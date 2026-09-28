"""
AetherMind Multimodal AI — Streamlit Native Web Application
Deployable directly to Streamlit Community Cloud (share.streamlit.io), Render, Railway, Hugging Face Spaces.
"""

import os
import sys
import asyncio
import streamlit as st

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app.providers.apiless import apiless_provider
from app.core.web_search_engine import web_search_engine

# Page Configuration
st.set_page_config(
    page_title="AetherMind Multimodal AI",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .chat-bubble {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.75rem;
    }
    .user-bubble {
        background-color: #1e293b;
        border-left: 4px solid #6366f1;
    }
    .ai-bubble {
        background-color: #0f172a;
        border-left: 4px solid #a855f7;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="main-header">🌌 AetherMind Multimodal AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Unlimited APIless AI Models • Real-Time Web Search • Multi-Language Support (50+ Languages)</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/sparkles.png", width=64)
    st.title("Settings & Models")
    
    selected_model = st.selectbox(
        "Select AI Model Engine",
        options=[
            "apiless-gpt4o (GPT-4o APIless)",
            "apiless-llama3 (LLaMA 3.3 70B)",
            "apiless-qwen (Qwen 2.5 Coder)",
            "apiless-deepseek (DeepSeek R1)",
            "apiless-mistral (Mistral Large)"
        ],
        index=0
    )
    
    enable_web_search = st.checkbox("🌐 Enable Real-Time Web Search", value=True)
    
    st.markdown("---")
    st.markdown("### 🌐 Supported Languages")
    st.caption("Auto-detects and responds in English, Telugu (తెలుగు), Hindi (हिंदी), Tamil, Bengali, Spanish, French, German & 50+ languages.")
    
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am **AetherMind Multimodal AI**. How can I help you today? You can ask me anything in any language, or request real-time web search information!"}
    ]

# Display Existing Chat Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask AetherMind anything..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⚡ *Thinking & processing response...*")

        async def get_response():
            full_prompt = prompt
            
            # Check for Real-Time Web Search
            if enable_web_search and web_search_engine.should_search(prompt):
                with st.spinner("🌐 Performing real-time DuckDuckGo web search..."):
                    search_context = await web_search_engine.search_and_format(prompt)
                    if search_context:
                        full_prompt = f"{search_context}\n\n[USER QUESTION]: {prompt}"

            # Call APIless AI Provider
            model_id = selected_model.split(" ")[0]
            messages_payload = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            messages_payload.append({"role": "user", "content": full_prompt})
            
            response_text = ""
            async for chunk in apiless_provider.generate_stream(messages=messages_payload, model=model_id):
                response_text += chunk
                message_placeholder.markdown(response_text + "▌")
            
            message_placeholder.markdown(response_text)
            return response_text

        # Run Async Response
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_response = loop.run_until_complete(get_response())
        
        # Save Assistant Response
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
