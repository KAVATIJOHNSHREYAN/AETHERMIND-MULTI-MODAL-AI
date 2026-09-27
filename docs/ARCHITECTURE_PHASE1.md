# 🚀 AetherMind Multimodal AI — Phase 1 Enterprise Architecture Blueprint

> **System Overview:** Single Unified Enterprise Multimodal AI Platform Architecture  
> **Architectural Paradigm:** Feature-Based, Layered, Repository & Provider Pattern with Unified Python Full-Stack Runtime  
> **Status:** Phase 1 Foundation Complete  

---

## 1. Complete Enterprise Folder Structure

```
AETHERMIND MULTIMODAL AI/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── audio.py
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   ├── health.py
│   │   │   ├── image.py
│   │   │   ├── memory.py
│   │   │   ├── profile.py
│   │   │   ├── providers.py
│   │   │   ├── search.py
│   │   │   ├── settings.py
│   │   │   ├── upload.py
│   │   │   ├── user.py
│   │   │   └── vision.py
│   │   ├── __init__.py
│   │   └── router.py
│   ├── audio/
│   │   ├── __init__.py
│   │   └── speech_engine.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── clerk.py
│   │   └── jwt.py
│   ├── chat/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── components/
│   │   ├── __init__.py
│   │   └── ui_registry.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── devtools/
│   │   ├── __init__.py
│   │   └── console.py
│   ├── documentation/
│   │   ├── __init__.py
│   │   └── swagger.py
│   ├── documents/
│   │   ├── __init__.py
│   │   └── rag_engine.py
│   ├── images/
│   │   ├── __init__.py
│   │   └── vision_engine.py
│   ├── logging/
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── memory/
│   │   ├── __init__.py
│   │   └── memory_engine.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── cors.py
│   │   ├── error_handler.py
│   │   └── logging_middleware.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── file.py
│   │   ├── memory.py
│   │   ├── message.py
│   │   ├── settings.py
│   │   └── user.py
│   ├── pages/
│   │   ├── __init__.py
│   │   └── views.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── ai_provider.py
│   │   ├── base.py
│   │   ├── image_provider.py
│   │   ├── speech_provider.py
│   │   └── vision_provider.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── chat_repository.py
│   │   ├── file_repository.py
│   │   ├── message_repository.py
│   │   └── user_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── common.py
│   │   ├── file.py
│   │   ├── memory.py
│   │   ├── message.py
│   │   ├── search.py
│   │   └── settings.py
│   ├── security/
│   │   ├── __init__.py
│   │   └── encryption.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   ├── image_service.py
│   │   ├── memory_service.py
│   │   └── storage_service.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── storage/
│   │   ├── __init__.py
│   │   └── supabase_client.py
│   ├── templates/
│   │   └── index.html
│   ├── testing/
│   │   ├── __init__.py
│   │   └── test_utils.py
│   ├── user/
│   │   ├── __init__.py
│   │   └── user_manager.py
│   ├── utilities/
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── vision/
│   │   ├── __init__.py
│   │   └── vision_engine.py
│   ├── __init__.py
│   └── main.py
├── docker/
│   └── docker-compose.yml
├── docs/
│   └── ARCHITECTURE_PHASE1.md
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 2. Complete Architecture Diagram

```mermaid
graph TD
    Client["User Interface Shell (Single Page Unified App)"] --> AppRouter["FastAPI Application Gateway (app/main.py)"]
    
    subgraph Single Unified Full Stack Application
        AppRouter --> CORS["Middleware Layer (Cors, Errors, Logging)"]
        CORS --> APIV1["API Gateway Router (/api/v1)"]
        
        APIV1 --> ChatAPI["Chat & Stream Controller (/api/v1/chat)"]
        APIV1 --> ImageAPI["Image & Vision Controller (/api/v1/image)"]
        APIV1 --> DocAPI["Document Intelligence Controller (/api/v1/document)"]
        APIV1 --> VoiceAPI["Audio & Speech Controller (/api/v1/audio)"]
        APIV1 --> MemoryAPI["Memory Controller (/api/v1/memory)"]
        
        ChatAPI --> ChatService["Chat Service Layer"]
        ImageAPI --> ImageService["Vision & Image Service"]
        DocAPI --> DocService["RAG & Document Service"]
        VoiceAPI --> VoiceService["Speech & Voice Service"]
        MemoryAPI --> MemoryService["Long-Term Vector Memory Service"]
        
        ChatService --> ProviderManager["AI Provider Abstraction Manager"]
        ImageService --> ProviderManager
        DocService --> ProviderManager
        VoiceService --> ProviderManager
        
        ChatService --> RepoLayer["Repository Layer (BaseRepository)"]
        MemoryService --> RepoLayer
        DocService --> RepoLayer
        
        RepoLayer --> ORM["SQLAlchemy Async ORM"]
    end
    
    subgraph Infrastructure Services
        ORM --> PostgreSQL[("PostgreSQL DB (Supabase / Local)")]
        DocService --> Qdrant[("Qdrant Vector DB (RAG & Context)")]
        MemoryService --> Qdrant
        ChatService --> Redis[("Redis Cache & Task Broker")]
        DocService --> SupabaseStore[("Supabase Object Storage")]
    end
```

---

## 3. Complete Module Dependency Diagram

```mermaid
graph LR
    subgraph "Core App Layer"
        Main["app/main.py"] --> Config["app/config/settings.py"]
        Main --> Router["app/api/router.py"]
        Main --> Logger["app/logging/logger.py"]
    end

    subgraph "Domain Engines"
        Router --> ChatEngine["app/chat/engine.py"]
        Router --> DocEngine["app/documents/rag_engine.py"]
        Router --> ImageEngine["app/images/vision_engine.py"]
        Router --> VoiceEngine["app/audio/speech_engine.py"]
        Router --> MemoryEngine["app/memory/memory_engine.py"]
    end

    subgraph "Provider & Service Interfaces"
        ChatEngine --> Providers["app/providers/base.py"]
        DocEngine --> Storage["app/storage/supabase_client.py"]
        MemoryEngine --> VectorDB["Qdrant Vector Client"]
    end

    subgraph "Database & Storage Layer"
        Services["app/services/"] --> Repositories["app/repositories/base.py"]
        Repositories --> Models["app/models/"]
        Models --> Session["app/database/session.py"]
        Session --> Base["app/database/base.py"]
    end
```

---

## 4. Database Blueprint

### Entity Relationship Specifications

```mermaid
erDiagram
    USERS ||--o{ CHATS : owns
    USERS ||--o{ FILES : uploads
    USERS ||--o{ FOLDERS : creates
    USERS ||--o| USER_SETTINGS : configures
    USERS ||--o{ PROVIDER_SETTINGS : sets_keys
    USERS ||--o{ MEMORY_METADATA : retains
    CHATS ||--o{ MESSAGES : contains
    CHATS ||--o| CONVERSATION_METADATA : tracks
    FOLDERS ||--o{ FILES : contains

    USERS {
        string id PK
        string clerk_id UK
        string email UK
        string full_name
        string avatar_url
        boolean is_active
        datetime created_at
    }

    CHATS {
        string id PK
        string user_id FK
        string title
        boolean is_pinned
        string selected_model
        text system_prompt
        datetime created_at
    }

    MESSAGES {
        string id PK
        string chat_id FK
        string role
        text content
        json attachments
        json media_metadata
        datetime created_at
    }

    FILES {
        string id PK
        string user_id FK
        string filename
        string file_type
        string mime_type
        bigint size_bytes
        string storage_path
        string vector_point_id
        datetime created_at
    }

    MEMORY_METADATA {
        string id PK
        string user_id FK
        string memory_key
        text memory_value
        string category
        float confidence_score
        string qdrant_vector_id
    }
```

---

## 5. API Blueprint

| Method | Endpoint Blueprint | Module | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | System Health | Verify platform status & dependencies |
| `GET` | `/api/v1/chat` | Chat Engine | List all user chat conversations |
| `POST` | `/api/v1/chat` | Chat Engine | Initialize new chat conversation session |
| `GET` | `/api/v1/chat/{chat_id}` | Chat Engine | Retrieve single chat context & settings |
| `DELETE`| `/api/v1/chat/{chat_id}` | Chat Engine | Delete conversation and memory context |
| `POST` | `/api/v1/chat/{chat_id}/messages` | Chat Engine | Stream message response from AI Assistant |
| `POST` | `/api/v1/image/generate` | Vision Engine | AI Image Generation interface |
| `POST` | `/api/v1/image/analyze` | Vision Engine | Vision AI Image understanding & QA |
| `POST` | `/api/v1/document/process` | RAG Engine | Document ingestion & vector indexing |
| `POST` | `/api/v1/audio/stt` | Speech Engine | Speech-to-Text audio transcription |
| `POST` | `/api/v1/audio/tts` | Speech Engine | Text-to-Speech audio synthesis |
| `POST` | `/api/v1/upload` | Storage | Unified file upload to Supabase Storage |
| `POST` | `/api/v1/memory` | Memory Engine | Long-term memory query & retrieval |
| `GET` | `/api/v1/settings` | Settings | Fetch user preferences & model defaults |

---

## 6. Configuration Blueprint

All system configuration is managed through standard environment variables mapped to `app/config/settings.py` via `pydantic-settings`:

- **Database Connection:** `DATABASE_URL=postgresql+asyncpg://...`
- **Vector Database:** `QDRANT_URL=http://localhost:6333`
- **Cache Broker:** `REDIS_URL=redis://localhost:6379/0`
- **Object Storage:** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_STORAGE_BUCKET`
- **Model Providers:** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_GEMINI_API_KEY`, `ELEVENLABS_API_KEY`
- **Authentication:** `CLERK_SECRET_KEY`, `CLERK_ISSUER_URL`

---

## 7. Development Standards

1. **Single Unified Application:** All code must exist inside the single root directory `AETHERMIND MULTIMODAL AI`. No separate frontend or backend subfolders.
2. **Asynchronous I/O First:** All database access must use AsyncSQLAlchemy with `asyncpg`. All external HTTP requests must use `httpx.AsyncClient`.
3. **Repository Pattern:** Direct SQL or ORM queries inside route controllers are strictly forbidden. All access must pass through `BaseRepository`.
4. **Provider Abstraction:** Code must never depend on specific LLM SDKs directly; calls must be dispatched through `BaseAIProvider`.

---

## 8. Coding Standards

- **Python Version:** 3.11+ strictly typed.
- **Type Annotations:** All functions, methods, and parameters must specify explicit type hints.
- **Formattings:** Standardized using `black` (line-length 100) and `ruff`.
- **Imports:** Absolute imports from `app.*` (e.g. `from app.config.settings import settings`).

---

## 9. Security Standards

1. **Secrets Security:** API keys must never be logged or stored in plain text. Provider keys in DB must use symmetric encryption (`app/security/encryption.py`).
2. **Environment Isolation:** Zero credentials checked into Git (`.env` listed in `.gitignore`).
3. **Storage Security:** All uploaded files sanitized and written to Supabase Storage with strict UUID paths.

---

## 10. Testing Standards

- **Test Suite Framework:** `pytest` with `pytest-asyncio`.
- **Test Categories:**
  - `tests/unit/`: Test utility functions, Pydantic schemas, and data transformers.
  - `tests/integration/`: Test repository CRUD, database session lifecycle, and provider mock interfaces.
  - `tests/e2e/`: Test complete FastAPI route controllers and response schema contracts.

---

## 11. Enterprise Development Roadmap

```mermaid
timeline
    title AetherMind Multimodal AI Development Stages
    Phase 1 : Complete Foundation & Architecture : Project Package Structure : Database ORM & Schemas : API Blueprints : Configuration & Docker setup
    Phase 2 : Core Chat Engine & Streaming : Provider Integrations (Gemini/OpenAI/Claude) : Web Search Integration : Message Stream Manager
    Phase 3 : Multimodal Media Engines : Image Generation & Vision AI : PDF Document Intelligence (RAG + Qdrant) : Voice Speech (STT/TTS)
    Phase 4 : Production Hardening & Auth : Clerk Authentication Flow : User Memory Engine : Production Deployments (Vercel/Railway/Supabase)
```

---

> [!IMPORTANT]
> **PHASE 1 COMPLETE.**  
> The foundation architecture is established. Awaiting user approval before proceeding to Phase 2.
