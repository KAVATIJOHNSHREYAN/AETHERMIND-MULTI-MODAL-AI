# 🔑 AetherMind Multimodal AI — API Key & Service Directory

> **Master Credentials & Environment Configuration Guide**  
> Complete table breakdown of all required, recommended, and optional API keys used across the **AetherMind Multimodal AI** system.

---

## 1. 🤖 Multimodal AI & Speech Provider API Keys

| Service / Model | Environment Variable Key Name | Purpose & Capabilities | Status / Priority | Official Portal Link |
| :--- | :--- | :--- | :--- | :--- |
| **✨ Google Gemini** | `GOOGLE_GEMINI_API_KEY` | Gemini 1.5 Pro, Flash, Gemini 2.0, Vision analysis, Audio AI & `text-embedding-004` vector embeddings. | `PRIMARY RECOMMENDED` | [Google AI Studio ↗](https://aistudio.google.com/) |
| **🤖 OpenAI** | `OPENAI_API_KEY` | GPT-4o, GPT-4o-mini, o1/o3 reasoning models, DALL-E 3 image generation & `text-embedding-3-small`. | `OPTIONAL` | [OpenAI Platform ↗](https://platform.openai.com/api-keys) |
| **🧠 Anthropic** | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet, Claude 3 Opus, and Claude 3.5 Haiku deep reasoning models. | `OPTIONAL` | [Anthropic Console ↗](https://console.anthropic.com/) |
| **🎙️ ElevenLabs** | `ELEVENLABS_API_KEY` | Ultra-realistic AI voice synthesis, text-to-speech, and voice cloning in Audio Studio. | `OPTIONAL` | [ElevenLabs Dashboard ↗](https://elevenlabs.io/) |

---

## 2. ⚡ Vector Search & Cloud Storage Credentials

| Service Name | Environment Variable | Purpose & Description | Default Value | Service Dashboard |
| :--- | :--- | :--- | :--- | :--- |
| **⚡ Qdrant Endpoint** | `QDRANT_URL` | Vector database URL for high-speed semantic search, document RAG, and memory retrieval. | `http://localhost:6333` | [Qdrant Cloud ↗](https://cloud.qdrant.io/) |
| **🔑 Qdrant API Key** | `QDRANT_API_KEY` | Authentication key for Qdrant Cloud cluster (leave empty for local container). | `""` (Local Container) | [Qdrant Cloud ↗](https://cloud.qdrant.io/) |
| **☁️ Supabase Key** | `SUPABASE_SERVICE_ROLE_KEY` | Service role key to manage cloud object storage buckets for user uploaded files & images. | `""` (Local Disk Storage) | [Supabase Console ↗](https://supabase.com/dashboard) |
| **🌐 Supabase URL** | `SUPABASE_URL` | Supabase project REST API endpoint URL. | `""` | [Supabase Console ↗](https://supabase.com/dashboard) |

---

## 3. 🛡️ Authentication & Infrastructure Connections

| Key / Variable | Type | Usage & Description | Requirement Status |
| :--- | :--- | :--- | :--- |
| **`SECRET_KEY`** | JWT & AES Secret | Master secret key used to sign JWT authentication tokens and encrypt user API keys. | `SYSTEM REQUIRED` |
| **`DATABASE_URL`** | PostgreSQL URI | Async connection string for PostgreSQL (`postgresql+asyncpg://...`). Auto-falls back to SQLite (`aethermind.db`). | `AUTO-FALLBACK` |
| **`REDIS_URL`** | Redis URI | Connection URI for Redis / Upstash Redis for caching, rate limiting, and async tasks. | `OPTIONAL` (`redis://localhost:6379/0`) |
| **`FIREBASE_API_KEY`** | Auth Key | Official Firebase Web API key for authentication & JWT session management. | `SYSTEM REQUIRED` |

---

## 📋 Quick Setup `.env` Configuration Template

```bash
# ==============================================================================
# AETHERMIND MULTIMODAL AI - UNIFIED ENVIRONMENT CONFIGURATION
# ==============================================================================

# Multimodal AI Provider API Keys
GOOGLE_GEMINI_API_KEY="AIzaSyYourGeminiKeyHere"
OPENAI_API_KEY="sk-proj-YourOpenAIKeyHere"
ANTHROPIC_API_KEY="sk-ant-YourAnthropicKeyHere"
ELEVENLABS_API_KEY="YourElevenLabsKeyHere"

# Vector Database & Storage
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
SUPABASE_URL=""
SUPABASE_SERVICE_ROLE_KEY=""

# Database & Cache Settings
DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/aethermind_v3"
REDIS_URL="redis://localhost:6379/0"

# Security Secret
SECRET_KEY="aethermind-enterprise-jwt-secret-key-super-secure-2026"
```

---

## 💡 How to Add API Keys in the Application UI

1. Open **AetherMind Multimodal AI** in your browser at `http://127.0.0.1:8000/`.
2. Click **System Settings** ⚙️ at the bottom of the left floating sidebar.
3. Enter your **Google Gemini**, **OpenAI**, **Anthropic**, or **ElevenLabs** API keys into the corresponding input fields.
4. Click **Save Settings**. Keys are encrypted on the server before storage.
