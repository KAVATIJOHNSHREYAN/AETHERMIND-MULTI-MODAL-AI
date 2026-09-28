<div align="center">

# 🧠 AetherMind Multimodal AI

### Enterprise-Grade Unified Multimodal AI Operating System & Identity Portal

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit App](https://img.shields.io/badge/Streamlit_Cloud-Live_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/)
[![Firebase](https://img.shields.io/badge/Firebase_Auth-v10-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-DC2626?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-37%2F37_Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](#-testing-suite)

**One Unified Multimodal Engine. Firebase Identity Authentication. Zero Key Hassles.**

Chat with AI, analyze images, generate HD artwork, transcribe voice, maintain long-term vector memory, organize projects, and search across everything — all in one seamless enterprise application powered by intelligent auto-routing.

[🌐 Live Streamlit Cloud Application](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/) • [🔥 Firebase Setup Guide](./FIREBASE_AUTHENTICATION_GUIDE.md) • [Features](#-core-features) • [Architecture](#-system-architecture) • [Quickstart](#-quickstart--installation)

</div>

---

## 🌟 What Is AetherMind?

**AetherMind Multimodal AI** is a full-stack, production-grade AI operating system that unifies text chat, image generation, vision analysis, voice transcription, document intelligence, and workspace management into a single dark glassmorphism web interface.

The core features include:
1. **Firebase 10.0 Authentication Engine**: Full support for Email/Password, 1-Click Instant Guest Sign-In, and Google / GitHub OAuth.
2. **Dedicated Login (`/login`) & Logout (`/logout`) Portals**: Full-screen authentication views and in-app login modals.
3. **AetherMind Auto-Routing AI Engine**: Intelligent API-less routing for text chat and image generation, alongside API support for premium models.
4. **Real-Time Web Search**: DuckDuckGo API-less live web integration with citations.
5. **Qdrant Vector RAG & Memory**: Long-term contextual memory and document retrieval.

---

## ⚡ Core Features

### 1. 🔐 Firebase Identity & Session Management
- **Firebase Auth v10 SDK**: Enterprise email/password auth, token revocation, and secure session management.
- **Instant Guest Sign-In**: 1-click anonymous authentication without registration.
- **OAuth Providers**: Integrated Google & GitHub social authentication.
- **Dedicated Login (`/login`) & Logout (`/logout`) Pages**: Complete security status reporting, token revocation, and session clearing.
- **Firebase Setup Guide**: Complete step-by-step setup documentation in [`FIREBASE_AUTHENTICATION_GUIDE.md`](./FIREBASE_AUTHENTICATION_GUIDE.md).

### 2. 💬 Unified AI Chat Engine (Auto-Routing)
- **Smart Auto-Router**: Automatically dispatches requests to free API-less models (Pollinations) for text chat and image generation.
- **Multi-Model Provider Support**: APIless (Pollinations), Google Gemini, OpenAI GPT-4o, Groq, DeepSeek, Mistral, and local providers.
- **Automatic Failover**: Automatic retries and failovers if a provider is unavailable.

### 3. 🌍 Real-Time Web Search & Multi-Language
- **DuckDuckGo Live Search**: Real-time web retrieval with automatic intent detection.
- **50+ Languages Supported**: Automatic language detection supporting all 22 official Indian languages and global languages.

### 4. 🎨 AI Image Generation & Vision AI
- **Pollinations AI Flux/Realism/Anime Engines**: High-resolution image synthesis from text prompts or chat triggers.
- **Vision AI & Document OCR**: Extract text and analyze scenes from uploaded media.

### 5. 🎙️ Voice & Audio Processing Studio
- **Web Audio Recorder**: Real-time voice recording with live waveform display.
- **Speech-to-Text**: Audio file upload and automated transcription.

### 6. 🧠 Qdrant Vector RAG & Knowledge Memory
- **Vector Document Storage**: Semantic document indexing and retrieval Q&A.
- **Long-Term Memory Dashboard**: Automatic memory extraction and preference pinning.

---

## 🏗️ System Architecture

```mermaid
graph TD
    A[Client User Browser] -->|FastAPI Web App| B[app/main.py]
    A -->|Streamlit Cloud| C[streamlit_app.py]
    
    subgraph Authentication Engine
        D[Firebase Auth v10 SDK]
        E[/login Route & Auth Modal]
        F[/logout Route & Cleanup Modal]
    end

    subgraph Multimodal AI Engine
        G[AetherMind Auto-Router]
        H[Pollinations API-less Text & Image]
        I[DuckDuckGo Web Search]
        J[Google Gemini / Multi-Provider APIs]
    end

    subgraph Storage & RAG Vector Memory
        K[Qdrant Vector Database]
        L[SQLite / Memory Database]
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

## 📁 Repository Structure

```
├── app/
│   ├── api/v1/          # FastAPI API Endpoints (Auth, Chat, Memory, Workspace, etc.)
│   ├── auth/            # Firebase, Clerk, and JWT session handling logic
│   ├── main.py          # FastAPI application server & routes (/login, /logout, /)
│   ├── static/          # Web assets (styles.css, app.js, auth.js, images)
│   └── templates/       # HTML templates (index.html, auth.html)
├── streamlit_app.py     # Standalone Streamlit Cloud launcher & client API bridge
├── tests/               # Pytest automated test suites (37 passing tests)
├── FIREBASE_AUTHENTICATION_GUIDE.md  # Step-by-step Firebase Auth setup instructions
├── README.md            # Repository documentation
└── requirements.txt     # Python project dependencies
```

---

## ⚡ Quickstart & Installation

### Local Full-Stack Setup (FastAPI + Python)

1. **Clone Repository & Set Up Virtual Environment**:
   ```bash
   git clone https://github.com/KAVATIJOHNSHREYAN/AETHERMIND-MULTI-MODAL-AI.git
   cd AETHERMIND-MULTI-MODAL-AI
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and set your credentials:
   ```env
   PORT=8000
   DEBUG=True
   FIREBASE_API_KEY=AIzaSyAetherMindMockFirebaseKey_v4
   ```

3. **Run Application**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - Main App: `http://localhost:8000`
   - Login Portal: `http://localhost:8000/login`
   - Logout Page: `http://localhost:8000/logout`

---

### Streamlit Cloud Launcher

To run the Streamlit application locally:
```bash
streamlit run streamlit_app.py
```

Live Cloud Application: [https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/](https://aethermind-multi-modal-ai-fwt8jmcqdbbmoahwveobze.streamlit.app/)

---

## 🧪 Testing Suite

Run the full pytest suite to verify system integrity:
```bash
pytest tests/
```
All **37 test suites** cover authentication, workspace lifecycle, memory RAG, and multimodal routing.

---

## 📄 Firebase Authentication Guide

For detailed steps on setting up Firebase Authentication (Email/Password, Anonymous Guest Mode, Google, GitHub OAuth, Authorized Domains), read [`FIREBASE_AUTHENTICATION_GUIDE.md`](./FIREBASE_AUTHENTICATION_GUIDE.md).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

*Copyright © 2026 AetherMind AI Team*
