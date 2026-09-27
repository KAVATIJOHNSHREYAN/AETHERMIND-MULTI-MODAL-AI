# AETHERMIND MULTIMODAL AI — API KEY & CREDENTIALS REQUIREMENTS GUIDE

This document provides a complete reference for all API keys, service credentials, secrets, and environment variables required or supported by **AetherMind Multimodal AI**.

---

## 1. Multimodal AI Provider API Keys

| Key Name | Description & Usage | Requirement Level | Where to Obtain |
| :--- | :--- | :--- | :--- |
| **`GOOGLE_GEMINI_API_KEY`** | Powers Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0, vision analysis, audio processing, and vector text embeddings (`text-embedding-004`). | **Recommended** (Primary Provider) | [Google AI Studio](https://aistudio.google.com/) |
| **`OPENAI_API_KEY`** | Powers GPT-4o, GPT-4o-mini, o1/o3 reasoning models, DALL-E 3 image generation, and OpenAI vector embeddings (`text-embedding-3-small`). | **Optional** (Required for OpenAI models & DALL-E) | [OpenAI Platform](https://platform.openai.com/api-keys) |
| **`ANTHROPIC_API_KEY`** | Powers Claude 3.5 Sonnet, Claude 3 Opus, and Claude 3.5 Haiku for deep reasoning and long-context documents. | **Optional** (Required for Anthropic models) | [Anthropic Console](https://console.anthropic.com/) |
| **`ELEVENLABS_API_KEY`** | Powers ultra-realistic text-to-speech voice generation, voice cloning, and audio output in the Audio Studio. | **Optional** (Required for ElevenLabs voices) | [ElevenLabs Dashboard](https://elevenlabs.io/) |

---

## 2. Vector Search & Cloud Storage Keys

| Key Name | Description & Usage | Requirement Level | Default / Fallback |
| :--- | :--- | :--- | :--- |
| **`QDRANT_API_KEY`** | API Key for Qdrant Cloud cluster used in production vector search, document RAG, and memory retrieval. | **Optional** (Only for Qdrant Cloud) | Blank for local Qdrant container |
| **`QDRANT_URL`** | Connection endpoint for Qdrant vector database. | **Required** | `http://localhost:6333` |
| **`SUPABASE_SERVICE_ROLE_KEY`** | Secret Service Role Key to manage cloud object storage buckets for user uploaded files, images, and audio. | **Optional** (Uses local disk storage if blank) | [Supabase Project Settings](https://supabase.com/dashboard) |
| **`SUPABASE_URL`** | Supabase project REST API endpoint. | **Optional** | Blank |

---

## 3. Authentication & Encryption Security Keys

| Key Name | Description & Usage | Requirement Level | Default / Fallback |
| :--- | :--- | :--- | :--- |
| **`SECRET_KEY`** | Master secret key used to sign JWT user authentication tokens and derive Fernet encryption keys for storing user API keys. | **Required** | Pre-configured secure default string in `app/config/settings.py` |
| **`CLERK_SECRET_KEY`** | Secret key for Clerk Authentication backend API integration. | **Optional** (Used when Clerk auth mode is enabled) | [Clerk API Keys](https://dashboard.clerk.com/) |
| **`CLERK_PUBLISHABLE_KEY`** | Public key for frontend Clerk Auth widget integration. | **Optional** | Mock test key pre-configured |

---

## 4. Database & Infrastructure Connections

| Key Name | Description & Usage | Requirement Level | Default / Fallback |
| :--- | :--- | :--- | :--- |
| **`DATABASE_URL`** | PostgreSQL connection string (`postgresql+asyncpg://user:pass@host:port/db`) for persistent database storage. | **Auto-fallback** | If PostgreSQL is offline, system automatically falls back to local SQLite (`aethermind.db`). |
| **`REDIS_URL`** | Connection URI for Redis / Upstash Redis used for background task queues and fast key-value caching. | **Optional** | `redis://localhost:6379/0` |

---

## 5. Setup & Configuration Guide

### Method A: Web Interface Settings Modal
1. Launch the application server (`python -m uvicorn app.main:app --port 8000`).
2. Navigate to `http://127.0.0.1:8000/`.
3. Click **System Settings** (gear icon) in the bottom sidebar.
4. Enter your API keys into the respective fields and click **Save Settings**. Keys are encrypted on the server before storage.

### Method B: Environment Variable File (`.env`)
Create or edit the `.env` file in the repository root directory (`c:\Users\johns\Documents\AETHERMIND MULTIMODAL AI\.env`):

```bash
# Multimodal AI Provider API Keys
GOOGLE_GEMINI_API_KEY="your-google-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
ELEVENLABS_API_KEY="your-elevenlabs-api-key"

# Vector Database & Storage
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
SUPABASE_URL=""
SUPABASE_SERVICE_ROLE_KEY=""

# Database & Cache
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/aethermind_v3"
REDIS_URL="redis://localhost:6379/0"

# Security
SECRET_KEY="aethermind-enterprise-jwt-secret-key-super-secure-2026"
```
