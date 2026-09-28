<div align="center">

# 🧠 AetherMind Multimodal AI — Enterprise AI Operating System

### Unified Multimodal AI Engine, Vector RAG & Firebase Identity Portal

#### **Created by Kavati John Shreyan**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit_Cloud-Live_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/)
[![Firebase](https://img.shields.io/badge/Firebase_Auth-v10-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-DC2626?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Tests](https://img.shields.io/badge/Tests-37%2F37_Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](#-testing-suite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**One Unified Multimodal Engine. Live Firebase Identity. Zero API Key Hassles.**

Chat with AI, analyze PDFs & documents, generate HD artwork, transcribe audio, maintain long-term vector memory, organize projects, and search across your entire workspace — all inside a stunning dark glassmorphism AI OS.

[🌐 Live Streamlit Cloud Application](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/) • [🔥 Firebase Setup Guide](./FIREBASE_AUTHENTICATION_GUIDE.md) • [Features](#-complete-feature-manifest) • [Architecture](#-system-architecture) • [API Reference](#-api-endpoints-reference) • [Quickstart](#-quickstart--installation)

</div>

---

## 🌟 What Is AetherMind?

**AetherMind Multimodal AI** is a production-grade, enterprise artificial intelligence operating system created by **Kavati John Shreyan**. It unifies text generation, document intelligence, vision OCR, AI image synthesis, voice recording & transcription, vector RAG memory, and project management into a single ultra-responsive web platform.

---

## ⚡ Complete Feature Manifest

### 🔐 1. Firebase Identity & Authentication Engine
- **Live Firebase Auth v10 Integration**: Powered by live Firebase web SDK credentials.
- **Email & Password Authentication**: Complete registration, login, token verification, and session persistence.
- **1-Click Instant Guest Sign-In**: Anonymous guest authentication for instant access without signing up.
- **Social OAuth Integration**: Google OAuth and Microsoft OAuth sign-in handlers.
- **Dedicated Portals**:
  - `/login`: Full-page glassmorphism authentication interface with interactive login/signup tab switcher.
  - `/logout`: Full-page session termination and cookie/token revocation view.
  - Top-Right User Profile Menu: Live user display name, avatar, and quick sign-out menu.
- **Detailed Setup Documentation**: Complete step-by-step instructions in [`FIREBASE_AUTHENTICATION_GUIDE.md`](./FIREBASE_AUTHENTICATION_GUIDE.md).

---

### 💬 2. Unified Multimodal Chat & Auto-Routing AI Engine
- **Smart Auto-Routing Engine**: Automatically dispatches requests to high-performance API-less models (Pollinations AI) by default — zero API keys required!
- **Multi-Model Provider Selector**:
  - `AetherMind Auto Engine (Smart Multimodal)` *(Default API-less model)*
  - `⚡ OpenAI GPT-4o Vision`
  - `🧠 Anthropic Claude 3.5 Sonnet`
  - `🚀 Groq Llama 3.3 70B (Ultra Fast)`
  - `DeepSeek R1 / V3` & `Mistral AI`
- **Instant Fallback Resilience**: Automatic model fallback and retries ensure 100% uptime even if a provider is busy.

---

### 📄 3. Document Analysis & Deep Intelligence Library
- **Comprehensive Document Support**: Reads and extracts content from **PDF, DOCX, CSV, Excel, TXT, JSON, Markdown, and PPTX**.
- **Real-Time Document Q&A**: Upload any document and type `"analyze document"` or ask direct questions to get immediate, detailed structural summaries, key insights, and data table breakdowns.
- **Document Intelligence Library Modal (`modal-doc-library`)**:
  - Live search bar to filter indexed documents by title or extension.
  - Top toolbar action button (`⚡ Upload Document`).
  - **1-Click "📄 Load Sample Specs"**: Instantly generates and indexes an enterprise architecture specification document (`AetherMind_Enterprise_AI_Architecture.md`) to populate the library.
  - In-browser document viewer with pagination controls.

---

### 🔍 4. Qdrant Vector RAG & Knowledge Base
- **Qdrant Vector Database Integration**: Converts uploaded documents and knowledge collections into high-dimensional embeddings for semantic similarity search.
- **Knowledge Base Modal (`modal-knowledge-base`)**:
  - Create custom vector knowledge collections.
  - Ingest documents into specific collections with status reporting.
  - Vector similarity search bar to test semantic retrieval accuracy.

---

### 🌍 5. Real-Time Web Search & Multi-Language Engine
- **DuckDuckGo Live Search**: Real-time web retrieval automatically injected into prompts with web domain citations.
- **50+ Languages Auto-Detection**: Supports all 22 official Indian languages (*Telugu, Hindi, Tamil, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, etc.*) and global languages.

---

### 🎨 6. Media Gallery & AI Artwork Generator
- **Pollinations AI Flux / Realism / Anime Engine**: Generate HD images from text prompts (`/api/v1/image/generate`).
- **Media Gallery Modal (`modal-media-gallery`)**:
  - Gallery grid showcasing generated artwork and uploaded images.
  - Full-screen image preview modal with 1-click image download.
  - Image starring and soft-deletion options.

---

### 🎙️ 7. Audio & Voice Studio
- **Web Microphone Voice Recorder**: Record voice notes directly from the browser with live visual indicators.
- **Audio File Transcription**: Upload audio files (`MP3, WAV, M4A, FLAC`) for speech-to-text transcription.
- **Audio Studio Modal (`modal-audio-library`)**: Dedicated audio library with embedded HTML5 audio players.

---

### 🧠 8. Long-Term Memory Dashboard & Memory Compression
- **Memory Dashboard Modal (`modal-memory-dashboard`)**: Store persistent user facts, preferences, and pinned memories.
- **Memory Compression (`/api/v1/memory/compress`)**: 1-click memory compression button in the topbar to condense long chat trajectories into key facts.

---

### 📁 9. Workspace Projects, Global Search & Recycle Bin
- **Projects & Folders Modal (`modal-projects`)**: Create project workspaces, organize files, and download bulk ZIP archives (`/api/v1/workspace/download-zip`).
- **Global Search Modal (`modal-global-search`)**: Unified workspace search querying across chats, files, images, documents, audio, projects, and long-term memory.
- **Recycle Bin Modal (`modal-recycle-bin`)**: Soft deletion safety net with 1-click file restoration or complete bin emptying.

---

### 📱 10. Multi-Device Viewport Switcher Engine
- **Top-Right Device Switcher Widget**: Toggle between 4 device viewports instantly:
  - 🖥️ **Desktop**: Full-width (`100%`) viewport.
  - 💻 **Laptop**: Centered `1280px` canvas.
  - 📱 **Tablet**: Centered `768px` canvas.
  - 📱 **Mobile Phone**: Compact `390px` mobile view.
- **Zero Bottom Cutoff Guarantee**: Responsive layout guarantees the bottom chat bar (`Attach`, `Camera`, `Generate`, `Voice`, `Send`) is 100% visible at all times on any monitor or zoom level.

---

### 🎨 11. High-Contrast Vibrant Neon Styling
- **Curated Color System**:
  - `.btn-primary`: Cyber Pink to Cyan gradient (`linear-gradient(135deg, #FF007A 0%, #7928CA 50%, #00DFD8 100%)`) with magenta glowing shadow.
  - `.btn-cyan`: Electric Cyan gradient (`linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%)`).
  - `.btn-secondary`: Electric Violet gradient (`linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)`).
  - `input[type="file"]::file-selector-button`: Cyan-Purple gradient pill with glowing hover effects.
- **Futuristic Globe Wallpaper**: High-resolution, crisp globe wallpaper with glassmorphism panels.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Client User Browser] -->|FastAPI Web Server| B[app/main.py]
    A -->|Streamlit Cloud Launcher| C[streamlit_app.py]
    
    subgraph Identity & Auth Portal
        D[Firebase Auth v10 SDK]
        E[/login Route & Auth Modal]
        F[/logout Route & Cleanup]
    end

    subgraph Multimodal Core Engine
        G[AetherMind Auto-Router]
        H[Pollinations API-less Text & Image]
        I[DuckDuckGo Live Web Search]
        J[Document OCR & Text Extractor]
    end

    subgraph Vector RAG & Memory Storage
        K[Qdrant Vector DB]
        L[SQLite Workspace & Memory DB]
    end

    B --> D
    C --> D
    B --> G
    C --> G
    G --> H
    G --> I
    G --> J
    B --> K
    B --> L
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/login` | Full-screen Firebase authentication portal | No |
| `GET` | `/logout` | Full-screen logout portal & cookie cleanup | No |
| `POST` | `/api/v1/auth/login` | Authenticates user credentials & returns JWT | No |
| `POST` | `/api/v1/auth/register` | Registers a new user account | No |
| `POST` | `/api/v1/auth/logout` | Revokes current user session token | Yes |
| `POST` | `/api/v1/chat` | Multimodal AI chat completion & document analysis | Yes |
| `POST` | `/api/v1/image/generate` | Generates AI artwork via Pollinations Flux | Yes |
| `POST` | `/api/v1/upload` | Uploads and indexes documents into Qdrant | Yes |
| `GET` | `/api/v1/workspace/doc-library` | Lists indexed document intelligence files | Yes |
| `GET` | `/api/v1/workspace/media-gallery` | Retrieves generated & uploaded media files | Yes |
| `GET` | `/api/v1/workspace/audio-library` | Lists audio recordings and voice notes | Yes |
| `POST` | `/api/v1/memory` | Stores persistent memory points & preferences | Yes |
| `POST` | `/api/v1/memory/compress` | Compresses chat trajectories into core memories | Yes |
| `POST` | `/api/v1/workspace/search` | Global workspace search across all entities | Yes |

---

## 📁 Repository Structure

```
├── app/
│   ├── api/v1/          # FastAPI REST endpoints (Auth, Chat, Image, Workspace, Memory)
│   ├── auth/            # Firebase SDK & JWT session management logic
│   ├── core/            # Multimodal auto-routing, image generator, and search engines
│   ├── main.py          # Main FastAPI app & web routes (/login, /logout, /)
│   ├── static/          # CSS styles, JS scripts (app.js, auth.js), and images
│   └── templates/       # HTML5 templates (index.html, auth.html)
├── tests/               # Pytest automated test suites (37/37 passing)
├── streamlit_app.py     # Standalone Streamlit Cloud runner & client API bridge
├── FIREBASE_AUTHENTICATION_GUIDE.md  # Firebase Auth setup step-by-step documentation
├── README.md            # Project documentation
└── requirements.txt     # Python backend dependencies
```

---

## ⚡ Quickstart & Installation

### Local Full-Stack Setup (FastAPI + Python)

1. **Clone Repository & Setup Virtual Environment**:
   ```bash
   git clone https://github.com/KAVATIJOHNSHREYAN/AETHERMIND-MULTI-MODAL-AI.git
   cd AETHERMIND-MULTI-MODAL-AI
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - App: `http://localhost:8000`
   - Login Portal: `http://localhost:8000/login`
   - Logout Page: `http://localhost:8000/logout`

---

### Streamlit Cloud Launcher

To run the Streamlit app locally:
```bash
streamlit run streamlit_app.py
```

Live Cloud URL: [https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/)

---

## 🧪 Testing Suite

Run the full pytest suite to verify system integrity:
```bash
pytest tests/
```
All **37 test suites** pass cleanly.

---

## 📄 Firebase Setup Guide

For step-by-step instructions on setting up Firebase Authentication (Email/Password, Guest Sign-In, OAuth Providers), refer to [`FIREBASE_AUTHENTICATION_GUIDE.md`](./FIREBASE_AUTHENTICATION_GUIDE.md).

---

## 📜 License & Author

Created and Maintained by **Kavati John Shreyan**.

Distributed under the MIT License. See `LICENSE` for details.

*Copyright © 2026 Kavati John Shreyan. All Rights Reserved.*
