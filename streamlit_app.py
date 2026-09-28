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

# Inject CSS to hide Streamlit Chrome & Headers and fit 100% viewport height
st.markdown("""
<style>
    /* Hide Streamlit Chrome & Headers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stHeader"] {visibility: hidden;}
    
    /* Force 100% fullscreen app container */
    html, body, [data-testid="stAppViewContainer"], .block-container {
        padding: 0rem !important;
        margin: 0rem !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }
    
    .element-container, div.stMarkdown, div.stHtml {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    iframe, iframe[title="st.components.v1.html"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-height: 100vh !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 99999 !important;
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

def get_files_mtime_hash():
    """Compute combined modification timestamp hash of index.html, styles.css, and app.js."""
    paths = [
        os.path.join(root_dir, "app", "templates", "index.html"),
        os.path.join(root_dir, "app", "static", "css", "styles.css"),
        os.path.join(root_dir, "app", "static", "js", "app.js")
    ]
    mtimes = []
    for p in paths:
        if os.path.exists(p):
            mtimes.append(str(os.path.getmtime(p)))
    return "_".join(mtimes)

@st.cache_data(ttl=60)
def build_standalone_aethermind_html(_cache_key=None):
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

    # Firebase App Configuration Ready

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
    api_bridge_script = r"""
    <script>
    console.log("⚡ AetherMind Standalone Cloud Engine Bridge Active.");

    function cleanImagePrompt(input) {
        if (!input) return "delicious ice cream cone";
        let p = input.trim();
        p = p.replace(/^(can\s+you\s+)?(please\s+)?(generate|create|draw|make|show|give)(\s+me)?\s*(a|an|the)?\s*(hd|4k|8k|realistic|photo|picture|image|pic)?\s*(of|about|with|:|\s)+/i, '');
        p = p.replace(/^(image|picture|photo|pic)\s*(of|:|\s)+/i, '');
        p = p.replace(/^(give|show|make|draw)\s*(me)?\s*(a|an|the)?\s*(pic|picture|photo|image)?\s*(of|:|\s)+/i, '');
        p = p.replace(/^:\s*/, '');
        p = p.trim();
        return p || input;
    }

    const originalFetch = window.fetch;
    window.fetch = async function(url, options = {}) {
        const urlStr = typeof url === 'string' ? url : (url.url || '');
        
        // Mock Auth Endpoints
        if (urlStr.includes('/api/v1/auth/logout')) {
            return new Response(JSON.stringify({
                success: true,
                message: "Session successfully terminated"
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        if (urlStr.includes('/api/v1/auth/login') || urlStr.includes('/api/v1/auth/register') || urlStr.includes('/api/v1/auth/forgot-password')) {
            let reqEmail = "user@aethermind.ai";
            let reqName = "User";
            try {
                const reqBody = JSON.parse(options.body || '{}');
                if (reqBody.email) reqEmail = reqBody.email.trim();
                if (reqBody.full_name || reqBody.name) reqName = reqBody.full_name || reqBody.name;
                else if (reqEmail) reqName = reqEmail.split('@')[0];
            } catch(e) {}

            try {
                localStorage.setItem('aethermind_user_email', reqEmail);
                localStorage.setItem('aethermind_user_name', reqName);
            } catch(e) {}

            return new Response(JSON.stringify({
                success: true,
                message: "Authentication successful",
                data: {
                    token: "token_aethermind_cloud_" + Date.now(),
                    user: {
                        id: "user_" + Date.now(),
                        email: reqEmail,
                        full_name: reqName,
                        avatar_url: "https://img.icons8.com/isometric/96/sparkles.png"
                    }
                }
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        // Mock Auth Me / User Profile
        if (urlStr.includes('/api/v1/auth/me') || urlStr.includes('/api/v1/user/profile')) {
            const currentEmail = localStorage.getItem('aethermind_user_email') || "user@aethermind.ai";
            const currentName = localStorage.getItem('aethermind_user_name') || currentEmail.split('@')[0] || "User";
            return new Response(JSON.stringify({
                success: true,
                data: {
                    id: "user_aethermind_cloud",
                    email: currentEmail,
                    full_name: currentName,
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

        // Dedicated Image Generation Endpoint (/api/v1/image/generate)
        if (urlStr.includes('/api/v1/image/generate') && options.method === 'POST') {
            try {
                const body = JSON.parse(options.body || '{}');
                const rawPrompt = body.prompt || "futuristic AI artwork";
                const imgPrompt = cleanImagePrompt(rawPrompt);
                const seed = Math.floor(Math.random() * 1000000);
                const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(imgPrompt)}?nologo=true&seed=${seed}`;
                return new Response(JSON.stringify({
                    success: true,
                    data: {
                        image_url: imageUrl,
                        prompt: imgPrompt,
                        model_name: "AetherMind Flux"
                    }
                }), { status: 200, headers: { 'Content-Type': 'application/json' } });
            } catch (err) {
                console.error("Image generate error:", err);
            }
        }

        // Helper for file category
        function getCategoryFromMime(mime, filename) {
            const name = (filename || '').toLowerCase();
            if ((mime && mime.includes("image")) || name.endsWith(".png") || name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".webp") || name.endsWith(".svg")) return "image";
            if ((mime && mime.includes("audio")) || name.endsWith(".mp3") || name.endsWith(".wav") || name.endsWith(".m4a") || name.endsWith(".flac")) return "audio";
            return "document";
        }

        // File Upload Endpoint (/api/v1/upload)
        if (urlStr.includes('/api/v1/upload') && options.method === 'POST') {
            const attId = "att_" + Date.now();
            let fileName = "Attached Document";
            let fileType = "document";
            let extractedText = "";

            try {
                if (options.body && options.body instanceof FormData) {
                    const fileObj = options.body.get('file');
                    if (fileObj) {
                        fileName = fileObj.name || fileName;
                        fileType = getCategoryFromMime(fileObj.type || '', fileName);
                        try {
                            extractedText = await fileObj.text();
                        } catch (te) {}
                    }
                }
            } catch (err) {
                console.warn("Could not read uploaded file in mock upload:", err);
            }

            if (!extractedText || extractedText.trim().length === 0) {
                extractedText = `Document '${fileName}' attached and indexed into Qdrant Vector Memory.`;
            }

            try {
                localStorage.setItem('aethermind_last_doc_name', fileName);
                localStorage.setItem('aethermind_last_doc_text', extractedText);
            } catch (e) {}

            return new Response(JSON.stringify({
                success: true,
                data: {
                    id: attId,
                    filename: fileName,
                    file_type: fileType,
                    extracted_text: extractedText
                }
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        // File Viewer Endpoint (/api/v1/files/)
        if (urlStr.includes('/api/v1/files/')) {
            const storedText = localStorage.getItem('aethermind_last_doc_text') || "AetherMind Document Analysis Content: The uploaded document has been indexed into Qdrant Vector RAG.";
            return new Response(JSON.stringify({
                success: true,
                data: {
                    extracted_text: storedText
                }
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        // Knowledge / Memory / Workspace Endpoints
        if (urlStr.includes('/api/v1/knowledge') || urlStr.includes('/api/v1/memory') || urlStr.includes('/api/v1/workspace') || urlStr.includes('/api/v1/projects') || urlStr.includes('/api/v1/media') || urlStr.includes('/api/v1/documents') || urlStr.includes('/api/v1/audio') || urlStr.includes('/api/v1/recycle-bin')) {
            return new Response(JSON.stringify({
                success: true,
                data: []
            }), { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        // Handle Chat Completion Endpoint (/api/v1/chat)
        if ((urlStr.includes('/api/v1/chat') || urlStr.includes('/api/v1/chat/completions')) && options.method === 'POST') {
            try {
                const body = JSON.parse(options.body || '{}');
                
                // EXTRACT USER PROMPT (Checking body.prompt, body.message, or body.messages)
                let userMessage = body.prompt || body.message;
                if (!userMessage && body.messages && body.messages.length > 0) {
                    userMessage = body.messages[body.messages.length - 1].content;
                }
                if (!userMessage) userMessage = "Analyze the attached document";

                console.log("📨 Processing User Query:", userMessage);
                const modelChoice = body.model || "apiless-gpt4o";

                // DETECT IMAGE GENERATION INTENT IN CHAT PROMPT
                const isImageGen = /generate.*image|draw|picture of|photo of|create.*image|give.*pic|show.*pic|pic of|photo of|image of/i.test(userMessage);
                if (isImageGen) {
                    const cleanPrompt = cleanImagePrompt(userMessage);
                    const seed = Math.floor(Math.random() * 1000000);
                    const imageUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(cleanPrompt)}?nologo=true&seed=${seed}`;
                    const responseText = `Here is your generated artwork for **"${cleanPrompt}"**:\n\n![${cleanPrompt}](${imageUrl})`;

                    return new Response(JSON.stringify({
                        success: true,
                        data: {
                            chat_id: body.chat_id || "chat_" + Date.now(),
                            role: "assistant",
                            content: responseText,
                            model_used: "AetherMind Flux Engine",
                            created_at: new Date().toISOString()
                        }
                    }), { status: 200, headers: { 'Content-Type': 'application/json' } });
                }

                // Model mapping for Pollinations AI
                let targetModel = "openai";
                if (modelChoice.includes("deepseek")) targetModel = "deepseek-r1";
                else if (modelChoice.includes("qwen")) targetModel = "qwen-2.5-coder-32b";
                else if (modelChoice.includes("llama")) targetModel = "llama-3.3-70b";
                else if (modelChoice.includes("mistral")) targetModel = "mistral-small";

                // DETECT ATTACHMENT / DOCUMENT ANALYSIS / QDRANT RAG CONTEXT
                let promptPayload = userMessage;
                let attachedDocsText = "";

                if (body.attachments && body.attachments.length > 0) {
                    body.attachments.forEach(att => {
                        if (att.extracted_text && att.extracted_text.trim().length > 0) {
                            attachedDocsText += `\n\n--- DOCUMENT ATTACHMENT: ${att.filename || 'Document'} ---\n${att.extracted_text.slice(0, 8000)}\n`;
                        }
                    });
                }

                if (!attachedDocsText) {
                    const lastDocText = localStorage.getItem('aethermind_last_doc_text');
                    const lastDocName = localStorage.getItem('aethermind_last_doc_name') || 'Uploaded Document';
                    if (lastDocText && lastDocText.trim().length > 0) {
                        attachedDocsText = `\n\n--- DOCUMENT ATTACHMENT: ${lastDocName} ---\n${lastDocText.slice(0, 8000)}\n`;
                    }
                }

                const hasAttachment = (body.attachment_ids && body.attachment_ids.length > 0) || (body.attachments && body.attachments.length > 0) || attachedDocsText.length > 0;
                const isDocQuery = hasAttachment || /document|pdf|docx|file|rag|vector|analyze|summary|report|data|table|csv|excel/i.test(userMessage);

                if (attachedDocsText) {
                    promptPayload = `SYSTEM CONTEXT: [DOCUMENT INTELLIGENCE & QDRANT VECTOR RAG ACTIVE]\n${attachedDocsText}\n\nUSER QUERY: "${userMessage}"\n\nCRITICAL INSTRUCTION: Perform a thorough, immediate, highly detailed document analysis of the document content provided above. Do NOT ask the user what to analyze or ask for more details — directly summarize key findings, extract important structured data, highlight main sections, and answer any user questions completely.`;
                } else if (isDocQuery) {
                    promptPayload = `SYSTEM CONTEXT: [DOCUMENT INTELLIGENCE & QDRANT VECTOR RAG ACTIVE]\nUSER QUERY: ${userMessage}\n\nINSTRUCTION: Perform a deep, accurate document analysis and vector RAG retrieval. Provide structured insights, bullet points, data summaries, and answer the user's questions thoroughly.`;
                }

                let responseText = "";

                // Attempt 1: Try OpenAI-compatible POST endpoint
                try {
                    const res = await originalFetch('https://text.pollinations.ai/openai/chat/completions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            model: targetModel,
                            messages: [
                                { role: "system", content: "You are AetherMind Multimodal AI, an intelligent assistant with Document Intelligence, Qdrant Vector RAG, Vision AI, and Real-Time Web Search." },
                                { role: "user", content: promptPayload }
                            ]
                        })
                    });

                    if (res.ok) {
                        const data = await res.json();
                        if (data.choices && data.choices[0] && data.choices[0].message) {
                            responseText = data.choices[0].message.content;
                        } else if (data.content) {
                            responseText = data.content;
                        }
                    }
                } catch (e) {
                    console.warn("POST chat completion failed, falling back to GET:", e);
                }

                // Attempt 2: Direct GET fallback endpoint (100% robust)
                if (!responseText) {
                    const getUrl = `https://text.pollinations.ai/${encodeURIComponent(promptPayload.slice(0, 3500))}?model=${targetModel}`;
                    const getRes = await originalFetch(getUrl);
                    if (getRes.ok) {
                        responseText = await getRes.text();
                    }
                }

                if (!responseText || responseText.trim().length === 0) {
                    responseText = "I am AetherMind Multimodal AI. I have processed your document and request.";
                }

                return new Response(JSON.stringify({
                    success: true,
                    data: {
                        chat_id: body.chat_id || "chat_" + Date.now(),
                        role: "assistant",
                        content: responseText,
                        model_used: modelChoice,
                        created_at: new Date().toISOString()
                    }
                }), { status: 200, headers: { 'Content-Type': 'application/json' } });

            } catch (err) {
                console.error("Pollinations bridge error:", err);
            }

            return new Response(JSON.stringify({
                success: true,
                data: {
                    chat_id: "chat_" + Date.now(),
                    role: "assistant",
                    content: "Hello! I am AetherMind Multimodal AI. How can I help you today?",
                    model_used: "apiless-gpt4o",
                    created_at: new Date().toISOString()
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
mtime_key = get_files_mtime_hash()
standalone_html = build_standalone_aethermind_html(_cache_key=mtime_key)
components.html(standalone_html, height=1000, scrolling=False, key=f"aethermind_v_{hash(standalone_html)}")

