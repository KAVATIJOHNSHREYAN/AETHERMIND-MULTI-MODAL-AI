<div align="center">

# 🧠 AetherMind Multimodal AI

### Enterprise-Grade Unified Multimodal AI Operating System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://aethermind-multimodal-ai.vercel.app)
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-DC2626?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-37%2F37_Passing-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](#-testing-suite)

**One Unified Multimodal Engine. Zero App Switching. Zero API Key Hassles.**

Chat with AI, analyze images, generate HD artwork, transcribe voice, maintain long-term memory, organize projects, and search across everything — all in one seamless enterprise application powered by intelligent auto-routing.

[🌐 Live Demo](https://aethermind-multimodal-ai.vercel.app) • [Features](#-core-features) • [Architecture](#-system-architecture) • [Quickstart](#-quickstart--installation) • [API Reference](#-api-reference)

</div>

---

## 🌟 What Is AetherMind?

**AetherMind Multimodal AI** is a full-stack, production-grade AI operating system that unifies text chat, image generation, vision analysis, voice transcription, document intelligence, and workspace management into a single glassmorphism web application.

The defining feature is **AetherMind's Auto-Routing Engine** — users never need to manually configure API keys for basic usage. The system intelligently routes requests to the best available AI model behind the scenes, using free API-less models for text chat and image generation, and premium API-based models only when needed for advanced multimodal tasks.

---

## ⚡ Core Features

### 1. 💬 Unified AI Chat Engine (Auto-Routing)
- **Smart Auto-Router**: Automatically dispatches requests to the best provider — free API-less models for text, premium APIs for multimodal.
- **13+ AI Providers**: APIless (Pollinations), Google Gemini, OpenAI GPT-4o, Anthropic Claude, Groq, DeepSeek, Mistral, OpenRouter, Together AI, Cohere, xAI Grok, Ollama (local), and LM Studio.
- **Automatic Failover**: If a provider returns a rate limit or error, the system silently retries and fails over to the next available provider.
- **Session Persistence**: Chat history is saved per-session using `X-Session-ID` headers, so conversations survive page reloads.

### 2. 🌍 Real-Time Web Search
- **Auto-Detection**: The system intelligently detects when your question needs live web data (news, prices, facts, tutorials, etc.).
- **DuckDuckGo Integration**: Free, API-less web search via DuckDuckGo — no API keys or subscriptions required.
- **Source Citations**: Search results are injected into the AI context, and responses include source URLs for verification.
- **Slash Commands**: Use `/search`, `/web`, or `/browse` to force a web search on any query.
- **Smart Triggers**: Keywords like "latest news", "how to", "what is", "price of", dates (2024-2027), and question marks auto-trigger search.

### 3. 🌐 Multi-Language Support (50+ Languages)
- **Auto-Detection**: The AI automatically detects the language of your message and responds in the same language.
- **All 22 Indian Languages**: Telugu, Hindi, Tamil, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu, Sanskrit, Konkani, Manipuri, Nepali, Bodo, Dogri, Maithili, Santali, Sindhi, Kashmiri.
- **30+ World Languages**: English, Spanish, French, German, Japanese, Chinese, Korean, Arabic, Russian, Turkish, Portuguese, Italian, Dutch, and many more.
- **Zero Configuration**: No language settings to change — just type in your language and the AI matches it automatically.

### 4. 🎨 AI Image Generation (Auto-Rotating Multi-Model)
- **Free API-less Image Engines**: Flux, Turbo, Realism, Anime, and 3D — all powered by Pollinations AI.
- **Smart Model Selection**: The system analyzes prompt keywords to auto-select the best engine (e.g., "anime girl" → Anime engine, "cinematic photo" → Realism engine).
- **Weighted Random Rotation**: For generic prompts, models are selected via weighted probability (Flux 40%, Turbo 25%, Realism 15%, Anime 10%, 3D 10%).
- **Aspect Ratios & Quality**: Support for `1:1`, `16:9`, `9:16`, `4:3`, `3:2` with Standard, HD, and Ultra quality tiers.
- **PIL Fallback**: If the external API is down, a local PIL canvas engine generates stylized placeholder artwork.

### 5. 👁️ Vision AI & OCR
- **Scene Understanding**: Upload any image for detailed analysis — object recognition, scene description, spatial relationships.
- **Advanced OCR**: Extract text from charts, tables, graphs, screenshots, handwritten notes, and documents.
- **Powered by**: Google Gemini 2.5 Flash Vision API for multimodal image understanding.

### 6. 🎙️ Voice & Audio Processing
- **Browser Audio Recording**: Built-in Web Audio API recorder with real-time waveform visualization.
- **Speech-to-Text Transcription**: Upload `.mp3`, `.wav`, `.m4a`, `.flac`, `.webm`, `.ogg`, `.aac`, `.opus` files.
- **WAV Header Parsing**: Automatic extraction of sample rate, channels, and duration metadata.

### 7. 📄 Document Intelligence & RAG
- **Supported Formats**: PDF, DOCX, CSV, Excel, TXT, Markdown.
- **Automatic Chunking**: Documents are split into semantically meaningful chunks for vector embedding.
- **RAG Q&A**: Ask questions about uploaded documents and receive context-aware answers.
- **Powered by**: Qdrant Vector Database for dense + sparse hybrid search.

### 8. 🧠 Long-Term Memory Dashboard
- **Autonomous Memory**: The system automatically extracts and stores key facts, preferences, and context from conversations.
- **Pin & Filter**: Pin important memories, search by content, and manage memory categories.
- **Contextual Continuity**: Memories are injected into future conversations for personalized, context-aware responses.

### 9. 📚 Knowledge Base & Collections
- **Custom Collections**: Organize documents into named Qdrant vector collections.
- **Hybrid Search**: Dense vector similarity + sparse keyword matching for optimal retrieval.
- **Semantic Search**: Full cross-collection semantic search with relevance scoring.

### 10. 📁 Cloud Workspace & Productivity
- **Projects & Folders**: Organize chats, files, and media into custom-colored project workspaces.
- **Media Gallery**: Visual grid of all uploaded images with quick preview and star filters.
- **Document Library**: Searchable library of all uploaded documents.
- **Audio Library**: Dedicated audio file manager with playback controls.
- **Storage Analytics**: Real-time storage meter, file distribution breakdown, and activity timeline.
- **Recycle Bin**: Soft-delete with instant restore and permanent purge options.
- **Bulk ZIP Downloads**: Multi-file select and single-click ZIP archive exports.

### 11. 🔐 Authentication & Security
- **JWT Authentication**: Secure token-based auth with registration, login, logout, and password reset.
- **Guest Sessions**: Anonymous users get persistent sessions via `X-Session-ID` without requiring signup.
- **Role-Based Access**: User profiles with roles, avatars, and enterprise-grade access control.

---

## 🏛️ System Architecture

```mermaid
graph TD
    Client[Browser Client — Glassmorphism UI] --> APIGateway[FastAPI Application Server]
    
    subgraph Auto-Routing Engine
        APIGateway --> ProviderMgr[AI Provider Manager]
        ProviderMgr --> AutoRouter[AetherMind Auto-Router]
        AutoRouter --> |Text Chat| APIless[APIless Engine — Pollinations AI]
        AutoRouter --> |Vision/Multimodal| PremiumAPI[Premium API — Gemini / OpenAI]
    end

    subgraph Free APIless Providers — No Keys Required
        APIless --> GPT4o[APIless GPT-4o]
        APIless --> Qwen[APIless Qwen]
        APIless --> Llama3[APIless LLaMA 3]
        APIless --> DeepSeek[APIless DeepSeek R1]
        APIless --> MistralFree[APIless Mistral]
    end

    subgraph Premium API Providers — Keys Optional
        PremiumAPI --> Gemini[Google Gemini 2.5]
        PremiumAPI --> OpenAI[OpenAI GPT-4o]
        PremiumAPI --> Claude[Anthropic Claude]
        PremiumAPI --> Groq[Groq — LLaMA / Mixtral]
        PremiumAPI --> Others[DeepSeek / Mistral / xAI / Cohere]
        PremiumAPI --> Local[Ollama / LM Studio — Local]
    end

    subgraph Image Generation — Auto-Rotating Models
        APIGateway --> ImageEngine[Image Generator Engine]
        ImageEngine --> Flux[AetherMind Flux]
        ImageEngine --> Turbo[AetherMind Turbo]
        ImageEngine --> Realism[AetherMind Realism]
        ImageEngine --> Anime[AetherMind Anime]
        ImageEngine --> ThreeD[AetherMind 3D]
    end

    subgraph Multimodal Engines
        APIGateway --> WebSearch[Real-Time Web Search — DuckDuckGo]
        APIGateway --> VisionEngine[Vision AI & OCR Engine]
        APIGateway --> AudioEngine[Voice Recorder & STT Engine]
        APIGateway --> DocEngine[Document Intelligence & RAG]
    end

    subgraph Memory & Knowledge RAG
        APIGateway --> MemoryEngine[Long-Term Memory Manager]
        APIGateway --> KnowledgeEngine[Knowledge Base Manager]
        APIGateway --> VectorSearch[Hybrid Vector Search]
        VectorSearch --> Qdrant[(Qdrant Vector DB)]
    end

    subgraph Cloud Workspace
        APIGateway --> ProjectMgr[Projects & Folders]
        APIGateway --> FileManager[File Manager & ZIP Export]
        APIGateway --> Dashboard[Storage Analytics Dashboard]
        APIGateway --> RecycleBin[Recycle Bin Manager]
    end

    subgraph Data Layer
        APIGateway --> DB[(PostgreSQL 16 / SQLite)]
        APIGateway --> Redis[(Redis 7 Cache)]
        APIGateway --> Storage[Local / Vercel Storage]
    end
```

---

## 🔌 APIs & Services Used

| Service | Purpose | Cost | API Key Required? |
|---|---|---|---|
| **DuckDuckGo** (`html.duckduckgo.com`) | Real-time web search for current information, news, and facts | 🟢 Free | ❌ No |
| **Pollinations AI** (`text.pollinations.ai`) | APIless unlimited text chat (GPT-4o, Qwen, LLaMA, DeepSeek, Mistral) | 🟢 Free | ❌ No |
| **Pollinations AI** (`image.pollinations.ai`) | APIless image generation (Flux, Turbo, Realism, Anime, 3D) | 🟢 Free | ❌ No |
| **Google Gemini** (`generativelanguage.googleapis.com`) | Vision AI, OCR, multimodal chat with attachments | 🟡 Free tier / Paid | ✅ Yes (for vision) |
| **OpenAI** (`api.openai.com`) | GPT-4o chat & vision (optional premium provider) | 🔴 Paid | ✅ Yes (optional) |
| **Anthropic** (`api.anthropic.com`) | Claude 3.5 Sonnet (optional premium provider) | 🔴 Paid | ✅ Yes (optional) |
| **Groq** (`api.groq.com`) | Ultra-fast LLaMA / Mixtral inference | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **DeepSeek** (`api.deepseek.com`) | DeepSeek R1 reasoning model | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **Mistral** (`api.mistral.ai`) | Mistral Large / Medium models | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **OpenRouter** (`openrouter.ai/api`) | Multi-model gateway (100+ models) | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **Together AI** (`api.together.xyz`) | Open-source model hosting | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **Cohere** (`api.cohere.ai`) | Command R+ chat & embeddings | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **xAI** (`api.x.ai`) | Grok models | 🔴 Paid | ✅ Yes (optional) |
| **Ollama** (`localhost:11434`) | Local LLM inference | 🟢 Free | ❌ No (local) |
| **LM Studio** (`localhost:1234`) | Local LLM inference | 🟢 Free | ❌ No (local) |
| **Qdrant** (`qdrant.tech`) | Vector database for RAG & knowledge search | 🟡 Free tier / Paid | ✅ Yes (optional) |
| **Supabase** (`supabase.co`) | Cloud storage for file uploads | 🟡 Free tier / Paid | ✅ Yes (optional) |

> **Key Insight**: AetherMind works completely out-of-the-box with **zero API keys** for text chat and image generation. API keys are only needed if you want to use premium multimodal features (vision analysis, advanced models) or external storage/database services.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.11+ / FastAPI | High-performance async API server |
| **Frontend** | Vanilla JS + Glassmorphism CSS | Premium dark-neon UI with micro-animations |
| **Templating** | Jinja2 | Server-side HTML rendering |
| **ORM** | SQLAlchemy 2.0 (async) | Database models & migrations |
| **Database** | PostgreSQL 16 / SQLite (fallback) | Relational data storage |
| **Vector DB** | Qdrant | Dense + sparse hybrid vector search |
| **Cache** | Redis 7 | Session caching & task broker |
| **HTTP Client** | HTTPX | Async API calls to AI providers |
| **Image Processing** | Pillow (PIL) | Image manipulation & fallback canvas |
| **Auth** | python-jose (JWT) + Passlib (bcrypt) | Token auth & password hashing |
| **Migrations** | Alembic | Database schema versioning |
| **Deployment** | Vercel (Serverless) / Docker | Production hosting |
| **Testing** | Pytest + pytest-asyncio | 37 unit & integration tests |
| **Linting** | Ruff + Black + MyPy | Code quality & type checking |

---

## 🚀 Quickstart & Installation

### Prerequisites
- **Python**: 3.11 or higher
- **Git**

### Local Setup (Development)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/KAVATIJOHNSHREYAN/AETHERMIND-MULTI-MODAL-AI.git
   cd AETHERMIND-MULTI-MODAL-AI
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables** *(optional)*:
   Copy `.env.example` to `.env` and add API keys for premium features:
   ```bash
   cp .env.example .env
   ```
   > **Note**: AetherMind works out-of-the-box with zero configuration! Text chat and image generation use free API-less providers. If no external database is configured, it automatically falls back to a local SQLite database.

5. **Run the Application**:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

6. **Open in Browser**:
   Navigate to `http://localhost:8000/`

---

## 🐳 Docker Deployment

AetherMind includes a production-ready `Dockerfile` and `docker-compose.yml` orchestrating FastAPI, PostgreSQL 16, Qdrant Vector DB, and Redis 7.

```bash
# Build and launch all containerized services
docker-compose up -d --build
```

Access the application at `http://localhost:8000/`.

---

## ☁️ Vercel Deployment

AetherMind is optimized for Vercel serverless deployment with zero configuration:

```bash
vercel --prod
```

The `vercel.json` configuration handles routing all requests through the FastAPI application server with a 60-second max execution time per request.

---

## 🧪 Testing Suite

Run the full pytest suite (37 unit & integration tests covering all modules):

```bash
pytest
```

```bash
# With coverage report
pytest --cov=app --cov-report=html
```

---

## 🛰️ API Reference

### Chat & AI

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/chat/completions` | `POST` | Send prompt for AI chat response (auto-routed) |
| `/api/v1/chat/conversations` | `GET` | List active chat conversations |
| `/api/v1/chat/conversations/{id}` | `GET` | Get conversation with full message history |
| `/api/v1/providers/list` | `GET` | List all registered AI providers and models |

### Image Generation & Vision

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/image/generate` | `POST` | Text-to-image generation (auto-rotating models) |
| `/api/v1/image/analyze` | `POST` | Vision AI analysis & OCR on uploaded images |
| `/api/v1/image/variation` | `POST` | Generate variation of an existing image |
| `/api/v1/image/history` | `GET` | Retrieve image generation history |
| `/api/v1/image/history/{id}` | `DELETE` | Delete an image history record |

### Audio & Voice

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/audio/transcribe` | `POST` | Speech-to-text audio transcription |

### Document Intelligence

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/document/upload` | `POST` | Upload & ingest document into RAG vector index |

### Memory & Knowledge

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/memory` | `GET / POST` | Manage long-term user memories |
| `/api/v1/knowledge/collections` | `GET / POST` | Knowledge base collection management |
| `/api/v1/search/semantic` | `POST` | Cross-entity semantic search |

### Workspace & Productivity

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/projects` | `GET / POST` | Create and manage workspace projects |
| `/api/v1/files/bulk-download` | `POST` | Download selected files as ZIP archive |
| `/api/v1/workspace/recycle-bin` | `GET` | List soft-deleted files |
| `/api/v1/workspace/search` | `POST` | Global workspace search |
| `/api/v1/dashboard/overview` | `GET` | Storage & usage analytics |

### Auth & User

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/register` | `POST` | User registration |
| `/api/v1/auth/login` | `POST` | User login (JWT token) |
| `/api/v1/auth/profile` | `GET / PUT` | View / update user profile |
| `/api/v1/auth/settings` | `GET / PUT` | User settings management |

---

## 📂 Project Structure

```
AETHERMIND-MULTI-MODAL-AI/
├── app/
│   ├── api/v1/             # API route handlers (chat, image, audio, auth, etc.)
│   ├── auth/               # JWT session manager & auth utilities
│   ├── core/               # Core engines (vision, audio, image generator, dependencies)
│   ├── config/             # Application configuration & settings
│   ├── database/           # Database session & connection management
│   ├── documents/          # Document processing & text extraction
│   ├── memory/             # Long-term memory management
│   ├── middleware/          # CORS, rate limiting, request logging
│   ├── models/             # SQLAlchemy ORM models (User, Chat, File, etc.)
│   ├── providers/          # AI provider integrations (13+ providers)
│   │   ├── apiless.py      # Pollinations AI free unlimited provider
│   │   ├── google_gemini.py # Google Gemini 2.5 Flash
│   │   ├── openai_claude.py # OpenAI GPT-4o & Anthropic Claude
│   │   ├── other_providers.py # Groq, DeepSeek, Mistral, xAI, etc.
│   │   ├── manager.py      # Auto-routing & failover orchestrator
│   │   └── registry.py     # Provider registration & model mapping
│   ├── schemas/            # Pydantic request/response models
│   ├── security/           # Password hashing & token validation
│   ├── static/             # Frontend assets (JS, CSS, images, uploads)
│   ├── storage/            # File storage management
│   ├── templates/          # Jinja2 HTML templates
│   ├── vector/             # Qdrant vector database integration
│   ├── workspace/          # Workspace & project management
│   └── main.py             # FastAPI application entry point
├── tests/                  # 37 unit & integration tests
├── alembic/                # Database migration scripts
├── docker/                 # Docker configuration files
├── docs/                   # Project documentation
├── api/index.py            # Vercel serverless entry point
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Multi-container orchestration
├── vercel.json             # Vercel deployment configuration
├── pyproject.toml          # Project metadata & tool configuration
└── LICENSE                 # MIT License
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Developed with ❤️ by **Kavati John Shreyan**

[⬆ Back to Top](#-aethermind-multimodal-ai)

</div>
