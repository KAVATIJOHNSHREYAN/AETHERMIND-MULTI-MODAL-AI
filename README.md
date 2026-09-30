<div align="center">

# 🧠 AetherMind Multimodal AI — Enterprise AI Operating System

### Unified Multimodal AI Engine, Qdrant Vector RAG & Firebase Identity Portal

#### **Created by Kavati John Shreyan**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit_Cloud-Live_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/)
[![Firebase](https://img.shields.io/badge/Firebase_Auth-v10-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-DC2626?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Tests](https://img.shields.io/badge/Tests-34%2F34_Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](#-testing-suite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**One Unified Multimodal Engine. Live Firebase Identity. Zero API Key Hassles.**

Chat with AI, analyze PDFs & multi-format documents, generate HD artwork with auto prompt enhancement, transcribe speech to text, maintain long-term vector memory, organize projects, and search across your entire workspace — all inside a stunning dark glassmorphism AI OS.

[🌐 Live Streamlit Cloud Application](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/) • [🔥 Firebase Setup Guide](./FIREBASE_AUTHENTICATION_GUIDE.md) • [About](#-about-aethermind) • [Features](#-complete-feature-manifest) • [API Reference](#-api-endpoints-reference) • [Quickstart](#-quickstart--installation)

</div>

---

## ℹ️ About AetherMind

AetherMind Multimodal AI is an enterprise-grade artificial intelligence operating system created by Kavati John Shreyan that seamlessly unifies text generation, document intelligence, vision OCR, AI image synthesis, voice recording and speech-to-text transcription, Qdrant vector memory, and workspace project management into a single responsive dark glassmorphic platform. Designed with zero API key dependencies, the system features a smart multimodal auto-routing engine that dynamically selects optimal free models while maintaining live Firebase Authentication supporting email credentials, Google OAuth popups or redirects, and instant guest demo access. Users can upload multi-format documents including PDF, DOCX, CSV, Excel, TXT, and PPTX to perform instant structural summaries, data extractions, and semantic vector similarity searches via Qdrant RAG, alongside real-time web search capabilities powered by DuckDuckGo and automatic multi-language understanding across fifty-plus languages including all twenty-two official Indian languages. The creative studio includes an enterprise AI image generation engine with automatic prompt enhancement, multi-model failover rotation across Flux, Turbo, Realism, Anime, 3D, and vector canvas renderers, complete with interactive download, lightbox preview, copy, regenerate, and HD upscale controls, while a ChatGPT-style speech-to-text voice pipeline converts user speech into active input text without file attachment leakage. AetherMind further empowers enterprise workflows through long-term memory compression, project workspace categorization, multi-device viewport toggling for desktop, laptop, tablet, and mobile, a global search modal, and a soft-deletion recycle bin for total control over workspace assets.

---

## ⚡ Complete Feature Manifest

### 🔐 1. Firebase Identity & Authentication Engine
- **Live Firebase Auth v10 SDK Integration**: Embedded live Firebase configuration with token verification and cookie session management.
- **Email & Password Authentication**: Full registration, login, token signing, and session persistence.
- **Google OAuth Sign-In**: Popup and redirect Google Authentication (`signInWithPopup` / `signInWithRedirect`) enforcing valid Firebase user objects before opening workspace.
- **Instant Demo Guest Mode**: 1-click guest authentication for instant evaluation.

### 🎨 2. Enterprise AI Image Generation System
- **Automatic Prompt Enhancement**: Expands simple prompts (*"panda eating bamboo"*) into rich artistic descriptors (*"Ultra realistic giant panda eating fresh green bamboo in a peaceful bamboo forest during golden hour, cinematic lighting, detailed fur, DSLR photography, depth of field, volumetric lighting, masterpiece, ultra high resolution"*).
- **Multi-Model Failover Rotation**: Automatically rotates across `AetherMind Flux`, `Turbo`, `Realism`, `Anime`, `3D`, and PIL/SVG Canvas backup renderers for 100% reliable image loading.
- **Interactive Action Toolbar**:
  - ⬇️ **Download**: Saves high-resolution artwork directly to local disk.
  - ⛶ **Fullscreen**: Displays image in an un-cropped lightbox modal.
  - 📋 **Copy**: Copies image URL or prompt to clipboard.
  - 🔗 **Open**: Opens original image source in a new tab.
  - 🔄 **Regenerate**: Re-runs generation with a fresh seed.
  - ⚡ **HD Upscale**: Generates 8K ultra high-definition resolution artwork.

### 🎙️ 3. ChatGPT-Style Voice Input & STT Engine
- **Browser Live Speech-to-Text**: Captures speech using the Web Speech API and backend STT endpoint (`/api/v1/audio/transcribe`).
- **Direct Input Placement**: Places transcribed text into `chatInput.value` dynamically without file attachment leakage or uploading audio recordings as document files.
- **Smart Spoken Request Classification**: Automatically detects whether spoken sentences request image generation, document retrieval, or general chat.

### 📄 4. Document Intelligence & Qdrant Vector RAG
- **Multi-Format Extraction**: Reads and indexes `PDF, DOCX, CSV, Excel, TXT, JSON, Markdown, PPTX`.
- **Instant Structural Summaries**: Generates data table extractions, bullet point highlights, and section citations.
- **Qdrant Vector Database RAG**: Ingests collections into high-dimensional vector embeddings for semantic retrieval.

### 🌍 5. Web Search & Multi-Language Support
- **DuckDuckGo Real-Time Search**: Automatic search query injection with source domain citations.
- **50+ Languages Auto-Detection**: Full support for all 22 official Indian languages (*Telugu, Hindi, Tamil, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, etc.*) and global languages.

### 📁 6. Workspace Projects & Enterprise Modals
- **Memory Compression**: 1-click compression of long chat histories into long-term vector facts.
- **Projects & Folders**: Workspace categorization with bulk ZIP download support (`/api/v1/workspace/download-zip`).
- **Global Search Modal**: Unified workspace search querying across chats, files, images, documents, audio, projects, and memories.
- **Device Viewport Switcher**: Toggle between Desktop (`100%`), Laptop (`1280px`), Tablet (`768px`), and Mobile (`390px`) viewports.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/login` | Full-screen Firebase authentication portal | No |
| `GET` | `/logout` | Full-screen logout portal & cookie cleanup | No |
| `POST` | `/api/v1/auth/login` | Authenticates user credentials & returns JWT | No |
| `POST` | `/api/v1/auth/register` | Registers a new user account | No |
| `POST` | `/api/v1/auth/logout` | Revokes current user session token | Yes |
| `POST` | `/api/v1/chat/completions` | Multimodal AI chat completion & image intent routing | Yes |
| `POST` | `/api/v1/image/generate` | Generates AI artwork with auto prompt enhancement | Yes |
| `POST` | `/api/v1/audio/transcribe` | Transcribes audio recordings to speech text | Yes |
| `POST` | `/api/v1/upload` | Uploads and indexes documents into Qdrant | Yes |
| `GET` | `/api/v1/workspace/doc-library` | Lists indexed document intelligence files | Yes |
| `GET` | `/api/v1/workspace/media-gallery` | Retrieves generated & uploaded media files | Yes |
| `GET` | `/api/v1/workspace/audio-library` | Lists audio recordings and voice notes | Yes |
| `POST` | `/api/v1/memory` | Stores persistent memory points & preferences | Yes |
| `POST` | `/api/v1/memory/compress` | Compresses chat trajectories into core memories | Yes |
| `POST` | `/api/v1/workspace/search` | Global workspace search across all entities | Yes |

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

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and populate required keys:
   ```bash
   cp .env.example .env
   ```

   **Environment Variables**:
   | Variable | Description |
   | :--- | :--- |
   | `FIREBASE_API_KEY` | Firebase Web API Key |
   | `FIREBASE_AUTH_DOMAIN` | Firebase Auth Domain |
   | `FIREBASE_PROJECT_ID` | Firebase Project ID |
   | `FIREBASE_STORAGE_BUCKET` | Firebase Storage Bucket |
   | `FIREBASE_MESSAGING_SENDER_ID` | Firebase Messaging Sender ID |
   | `FIREBASE_APP_ID` | Firebase Web App ID |
   | `FIREBASE_MEASUREMENT_ID` | Firebase Measurement ID |
   | `SECRET_KEY` | JWT Secret Key for token signing |
   | `DATABASE_URL` | SQLite / PostgreSQL connection URI |
   | `QDRANT_URL` | Qdrant Vector DB HTTP endpoint |
   | `REDIS_URL` | Redis server URI |

3. **Run Server**:
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
All **34 test suites** pass cleanly.

---

## 📜 License & Author

Created and Maintained by **Kavati John Shreyan**.

Distributed under the MIT License. See `LICENSE` for details.

*Copyright © 2026 Kavati John Shreyan. All Rights Reserved.*
