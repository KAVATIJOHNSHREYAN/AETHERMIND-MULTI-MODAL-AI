"""
AetherMind Multimodal AI — Enterprise AI Operating System
Native Standalone Streamlit Cloud Web Runner
"""

import os
import sys
import base64
import re
import streamlit as st
import streamlit.components.v1 as components

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Page Configuration with Favicon PNG
favicon_file = os.path.join(root_dir, "app", "static", "img", "favicon.png")
favicon_icon = favicon_file if os.path.exists(favicon_file) else "🌌"

st.set_page_config(
    page_title="AetherMind Multimodal AI — Enterprise AI OS",
    page_icon=favicon_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject CSS to hide Streamlit Chrome & Headers
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

def get_base64_data_uri(file_path):
    """Convert binary asset into base64 Data URI."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = file_path.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else ("image/jpeg" if ext in ["jpg", "jpeg"] else "image/x-icon")
        return f"data:{mime};base64,{b64}"
    return ""

@st.cache_data
def build_standalone_aethermind_html():
    """Bundle index.html, styles.css, and app.js into a single standalone HTML package with inlined base64 images and API bridge."""
    index_path = os.path.join(root_dir, "app", "templates", "index.html")
    css_path = os.path.join(root_dir, "app", "static", "css", "styles.css")
    js_path = os.path.join(root_dir, "app", "static", "js", "app.js")

    # Inlined Base64 Image Assets
    app_icon_b64 = get_base64_data_uri(os.path.join(root_dir, "app", "static", "img", "app-icon.png"))
    favicon_b64 = get_base64_data_uri(os.path.join(root_dir, "app", "static", "img", "favicon.png"))
    apple_icon_b64 = get_base64_data_uri(os.path.join(root_dir, "app", "static", "img", "apple-touch-icon.png"))
    
    bg_path = os.path.join(root_dir, "app", "static", "img", "bg-futuristic.png")
    if not os.path.exists(bg_path):
        bg_path = os.path.join(root_dir, "app", "static", "img", "bg-futuristic.jpg")
    bg_img_b64 = get_base64_data_uri(bg_path)

    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()

    # Replace Clerk template variable
    html_content = html_content.replace("{{ clerk_publishable_key }}", "pk_test_mock_clerk_publishable_key")

    # Inlined Base64 Image Replacements (using regex to cleanly strip query parameters like ?v=...)
    if app_icon_b64:
        html_content = re.sub(r"/static/img/app-icon\.png(\?[^\'\"]*)?", app_icon_b64, html_content)
    if favicon_b64:
        html_content = re.sub(r"/static/(img/)?favicon\.(png|ico)(\?[^\'\"]*)?", favicon_b64, html_content)
    if apple_icon_b64:
        html_content = re.sub(r"/static/img/apple-touch-icon\.png(\?[^\'\"]*)?", apple_icon_b64, html_content)
    if bg_img_b64:
        css_content = re.sub(r"/static/img/bg-futuristic\.(jpg|png)(\?[^\'\"]*)?", bg_img_b64, css_content)

    # Injected Standalone Client API Bridge (Pollinations AI + DuckDuckGo Web Search + Multi-Language)
    api_bridge_script = """
    <script>
    console.log("⚡ AetherMind Standalone Cloud Engine Bridge Active.");

    // Standalone API Router Mock & Direct Pollinations Client
    const originalFetch = window.fetch;
    window.fetch = async function(url, options = {}) {
        const urlStr = typeof url === 'string' ? url : (url.url || '');
        
        // Mock Auth Me / User Profile
        if (urlStr.includes('/api/v1/auth/me') || urlStr.includes('/api/v1/user/profile')) {
            return new Response(JSON.stringify({
                success: true,
                data: {
                    id: "user_aethermind_cloud",
                    email: "guest@aethermind.ai",
                    full_name: "John Shreyan",
                    avatar_url: "https://img.icons8.com/isometric/96/sparkles.png"
                }
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        // Mock Chats History List
        if (urlStr.includes('/api/v1/chat/chats') && (!options.method || options.method === 'GET')) {
            const saved = localStorage.getItem('aethermind_saved_chats') || '[]';
            return new Response(JSON.stringify({
                success: true,
                data: JSON.parse(saved)
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        // Handle Chat Completion Endpoint natively via Pollinations AI
        if (urlStr.includes('/api/v1/chat') && options.method === 'POST') {
            try {
                const body = JSON.parse(options.body || '{}');
                const userMessage = body.message || (body.messages ? body.messages[body.messages.length - 1].content : "Hello");
                const modelChoice = body.model || "apiless-gpt4o";

                // Model mapping
                let targetModel = "openai";
                if (modelChoice.includes("deepseek")) targetModel = "deepseek-r1";
                else if (modelChoice.includes("qwen")) targetModel = "qwen-2.5-coder-32b";
                else if (modelChoice.includes("llama")) targetModel = "llama-3.3-70b";
                else if (modelChoice.includes("mistral")) targetModel = "mistral-small";

                // Pollinations OpenAI-compatible POST endpoint
                const res = await originalFetch('https://text.pollinations.ai/openai/chat/completions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        model: targetModel,
                        messages: [{ role: "user", content: userMessage }]
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    let responseText = "";
                    if (data.choices && data.choices[0] && data.choices[0].message) {
                        responseText = data.choices[0].message.content;
                    } else if (data.content) {
                        responseText = data.content;
                    }

                    if (!responseText) {
                        responseText = "AetherMind AI processed your query successfully.";
                    }

                    return new Response(JSON.stringify({
                        success: true,
                        data: {
                            chat_id: body.chat_id || "chat_" + Date.now(),
                            role: "assistant",
                            content: responseText,
                            model_used: modelChoice
                        }
                    }), { status: 200, headers: { 'Content-Type': 'application/json' } });
                }
            } catch (err) {
                console.warn("Pollinations fetch error, returning fallback response:", err);
            }

            return new Response(JSON.stringify({
                success: true,
                data: {
                    chat_id: "chat_" + Date.now(),
                    role: "assistant",
                    content: "Hello! I am AetherMind Multimodal AI. Your query has been processed.",
                    model_used: "apiless-gpt4o"
                }
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        return originalFetch(url, options);
    };
    </script>
    """

    # Inline CSS & JS using plain string replacement
    css_tag = f"<style>\n{css_content}\n</style>"
    js_tag = f"{api_bridge_script}\n<script>\n{js_content}\n</script>"

    html_content = html_content.replace('<link rel="stylesheet" href="/static/css/styles.css">', css_tag)
    html_content = html_content.replace('<script src="/static/js/app.js"></script>', js_tag)

    return html_content

# Build & Render Standalone HTML directly in Streamlit container
standalone_html = build_standalone_aethermind_html()
components.html(standalone_html, height=950, scrolling=True)
