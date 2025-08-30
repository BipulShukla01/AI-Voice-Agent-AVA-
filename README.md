<p align="center">
  <img src="/static/icons/icon-192.png" width="84" height="84" alt="AVA logo" />
</p>

<h1 align="center">AVA — Advanced Voice Assistant</h1>

<p align="center">
  A futuristic, PWA-ready voice assistant with a cinematic UI, real-time AI, and smart playback control.
  <br/>Speak naturally, see live transcriptions, hear lifelike replies, and preview music — all in one sleek UI.
</p>

<p align="center">
  <a href="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" /></a>
  <a href="https://img.shields.io/badge/FastAPI-⚡-009688?logo=fastapi&logoColor=white"><img src="https://img.shields.io/badge/FastAPI-⚡-009688?logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://img.shields.io/badge/PWA-Ready-5A0FC8?logo=pwa&logoColor=white"><img src="https://img.shields.io/badge/PWA-Ready-5A0FC8?logo=pwa&logoColor=white" alt="PWA Ready" /></a>
  <a href="https://img.shields.io/badge/License-OSS-2ea44f"><img src="https://img.shields.io/badge/License-OSS-2ea44f" alt="License" /></a>
</p>

---

## ✨ Highlights

- **Conversational voice chat** with session memory
- **Text-only chat** for accessibility and quick testing
- **Music previews** via Spotify (with iTunes fallback)
- **Smart playback control** (barge‑in) between Murf TTS and Spotify
- **Beautiful, animated UI** (particles, waves, breathing avatar)
- **Installable PWA** with offline-safe assets and screenshots
- **Pluggable API keys** via UI with optional local encryption

<div align="center">
  <img src="/static/screenshot-wide.png" alt="AVA wide screenshot" width="85%" style="border-radius: 12px;" />
  <br/>
  <sub>Modern, cinematic UI designed for both desktop and mobile.</sub>
</div>

---

## 🧭 Table of Contents

1. [Quickstart](#-quickstart-local)
2. [Environment & Config](#-environment--config)
3. [Architecture Overview](#-architecture-overview)
4. [Core Features](#-core-features)
   - [Assistant Persona](#-assistant-persona)
   - [Session Persistence (SQLite)](#-session-persistence-sqlite)
   - [API Keys (Dual Source + Encryption)](#-api-keys--dual-source--optional-encryption)
   - [Web Search (Tavily)](#-web-search-skill-tavily)
   - [Music Search & Previews](#-music-search--previews)
   - [Speech & Audio Pipeline](#-speech--audio-pipeline)
   - [PWA & Caching](#-pwa--caching)
5. [Playback Control (Barge‑In)](#-playback-control-barge-in)
6. [API Reference (Core)](#-api-reference-core)
7. [Project Structure](#-project-structure)
8. [Screenshots](#-screenshots)
9. [Testing](#-testing)
10. [Deployment](#-deployment)
11. [Security Considerations](#-security-considerations)
12. [Data Files](#-data-files)
13. [Developer Notes](#-developer-notes)
14. [Roadmap](#-roadmap)
15. [License](#-license)

---

## 🚀 Quickstart (Local)

Prerequisites: Python 3.10+

```powershell
# Windows PowerShell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Add your keys to uploads/.env (see Environment)
python main.py
# Open http://localhost:8000
```

```bash
# macOS/Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Add your keys to uploads/.env (see Environment)
python main.py
# Open http://localhost:8000
```

> Tip: In production on a single instance (Render Free/Starter), keep a single worker for WebSockets and in-memory sessions:
>
> `gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app`
>
> If you scale horizontally (multiple instances), move session state to Redis/DB and enable sticky sessions before increasing workers.

---

## 🔐 Environment & Config

Create `uploads/.env`:

```ini
MURF_API_KEY=your_murf_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
GEMINI_API_KEY=your_gemini_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
TAVILY_API_KEY=your_tavily_key
WEATHER_API_KEY=your_weather_key
# Optional — used to derive an encryption key for local key storage
SECRET_KEY=your_random_secret_for_encryption
```

- Keys are loaded via `dotenv` in `main.py` and can be overridden via the in‑app settings modal.
- Optional local encryption is used for UI‑supplied keys when `cryptography` is available.
- Missing keys degrade gracefully (e.g., TTS falls back to `static/fallback.mp3`).

---

## 🧩 Architecture Overview

```mermaid
sequenceDiagram
  autonumber
  participant U as User
  participant B as Browser (AVA UI)
  participant API as FastAPI Backend
  participant STT as AssemblyAI (STT)
  participant LLM as Google Gemini (LLM)
  participant TTS as Murf AI (TTS)

  U->>B: Speak
  B->>API: POST /llm/query (audio + session_id)
  API->>STT: Transcribe audio
  STT-->>API: transcript
  API->>LLM: Chat (w/ session history)
  LLM-->>API: llmResponse
  API->>TTS: Generate voice
  TTS-->>API: audioFile (mp3)
  API-->>B: { transcript, llmResponse, audioFile }
  B-->>U: Show text + play audio
```

- **Text‑only flow**: `POST /llm/text-query` → returns `{ llmResponse }`.
- **Session storage**: in-memory by `session_id` (swap for Redis/DB as needed).

---

## 🧱 Core Features

### 🧠 Assistant Persona

- **System prompt**: AVA’s identity, tone, and behavior are defined by a comprehensive system prompt (see `AVA_SYSTEM_PROMPT` in `main.py`).
- **Style**: warm, concise, empathetic; stays in character; light humor; boundaries for safe responses.

### 💾 Session Persistence (SQLite)

- When SQLAlchemy is available, AVA persists sessions and messages to `uploads/ava_data.db`.
- **Models**: `sessions` and `messages` with timestamps, pin/archive flags, and auto-titling.
- Falls back gracefully when SQLAlchemy is unavailable (in‑memory only).

#### Sessions API

- **POST /sessions** → `{ id, title, pinned, archived }`
- **GET /sessions** → `{ sessions: [...] }` (optional `?q=` search, `?pinned=1`)
- **GET /sessions/{session_id}/messages** → `{ messages: [...] }`
- **PATCH /sessions/{session_id}** (JSON: `{ title?, pinned?, archived? }`) → `{ ok: true }`
- **DELETE /sessions/{session_id}** → `204 No Content`

### 🔑 API Keys — Dual Source + Optional Encryption

- Keys are resolved from either `uploads/.env` or the **in‑app settings** (UI overrides env).
- Optional local encryption for UI‑provided keys when `cryptography` is installed.
  - If `SECRET_KEY` is set in env, a stable 32‑byte key is derived for encryption.
  - Otherwise a local key file is generated at `uploads/.config.key`.
- Encrypted config is stored at `uploads/config.json`.

#### Config Endpoints

- **POST /config/api-keys** (JSON map of key → value) — saves keys in memory and securely to disk; also reconfigures dependent SDKs (Gemini, AssemblyAI) live.
- **GET /config/api-keys** → `{ user: {..}, env: {..}, encryption_active: bool }` (booleans indicate presence only, not secret values).

### 🔎 Web Search Skill (Tavily)

- Integrated **Tavily** search for concise answers with top sources (requires `TAVILY_API_KEY`).
- Returns an answer followed by a short “Sources” list; fails gracefully on API errors.

### 🎵 Music Search & Previews

- **Spotify search** with market targeting and `include_external=audio` to maximize preview availability.
- **Token caching** using Client Credentials flow to reduce latency and rate‑limits.
- **iTunes fallback** provides 30‑second previews when Spotify credentials are missing or previews are unavailable.
- The UI supports quick play/stop and respects barge‑in rules.

### 🔊 Speech & Audio Pipeline

- **AssemblyAI** for speech‑to‑text; API key loaded at startup and can be updated at runtime via config endpoints.
- **Murf TTS** for natural‑sounding responses; falls back to a bundled `static/fallback.mp3` when keys are missing.
- **Barge‑in** orchestration between mic recording, Murf, and Spotify prevents overlapping audio.

### 📦 PWA & Caching

- Installable PWA with manifest, icons, and screenshots.
- `sw.js` implements a balanced caching strategy: cached static assets, network‑first for application code to keep updates fresh.

---

## 🎚️ Playback Control (Barge‑In)

To keep the experience natural and interruption‑friendly, AVA enforces:

- **Murf → Spotify**: If Murf TTS is playing, Spotify preview is paused.
- **Spotify → Murf**: If Spotify preview starts, Murf TTS stops.
- **User speech → All off**: When the mic is listening or speech is detected, any current playback (Murf/Spotify) stops immediately and the recording pipeline continues.

This prevents overlapping audio and ensures fast barge‑in during conversation.

---

## 📡 API Reference (Core)

Base URL: `http://localhost:8000`

- **GET /**
  - Serves the main UI

- **POST /generate-audio/**
  - JSON: `{ "text": string }`
  - Returns `{ audioFile }` (Murf TTS or fallback)

- **POST /tts/echo/**
  - Form‑Data: `file`
  - Returns `{ transcription, audioFile }`

- **POST /llm/query**
  - Form‑Data: `file`, `session_id`
  - Returns `{ userTranscription, llmResponse, audioFile }`

- **POST /llm/text-query**
  - JSON: `{ text, session_id }`
  - Returns `{ llmResponse }`

- **POST /chat/clear**
  - JSON: `{ session_id }`
  - Clears in‑memory history

---

## 🗂️ Project Structure

```
AVA/
├─ main.py                      # FastAPI app: routes, skills, integrations
├─ templates/
│  └─ index.html                # Single‑page UI
├─ static/
│  ├─ script.js                 # Frontend logic (tabs, recording, chat, playback)
│  ├─ audio-worklet-processor.js# AudioWorklet to stream Float32 frames
│  ├─ manifest.json             # PWA manifest
│  ├─ icons/                    # PWA icons
│  ├─ screenshot-*.png          # PWA screenshots
│  └─ fallback.mp3              # Safe audio fallback
├─ sw.js                        # Service worker (network-first for code, cached assets)
├─ uploads/
│  ├─ .env                      # Local environment variables
│  └─ .env.example              # Example template
├─ requirements.txt             # Python dependencies
├─ render.yaml                  # Example deployment config
├─ test_ai_chat.py              # Quick API smoke test
└─ README.md                    # You are here
```

---

## 🖼️ Screenshots

<div align="center">
  <img src="/static/screenshot-wide.png" alt="Wide screenshot" width="85%" style="border-radius: 12px;" />
  <br/>
  <img src="/static/screenshot-normal.png" alt="Normal screenshot" width="45%" style="border-radius: 12px; margin-top: 12px;" />
</div>

---

## 🧪 Testing

```bash
python test_ai_chat.py
```
Ensure the server is running at `http://localhost:8000`.

---

## ☁️ Deployment

- Set secrets securely (never commit `.env`).
- Example production command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

- Reverse proxy (e.g., Nginx) should pass WebSocket and static routes.
- For multi‑instance or long sessions, persist chat sessions (e.g., Redis).

---

## 🔐 Security Considerations

- Do not commit `uploads/.env`, `uploads/config.json`, or `uploads/.config.key`.
- Production deployments should use managed secrets and HTTPS.
- If running multiple instances or behind a load balancer, enable sticky sessions or move session state fully to a shared DB/Redis.

---

## 🗃️ Data Files

- **Database**: `uploads/ava_data.db` (created automatically when SQLAlchemy is available)
- **Key files**: `uploads/config.json` (encrypted/plain depending on availability), `uploads/.config.key` (when `SECRET_KEY` not provided)

---

## 🧰 Developer Notes

- **Testing**: `test_ai_chat.py` provides a quick smoke test for key endpoints.
- **Logging**: Key integrations print concise success/error markers in the server logs (e.g., Spotify token fetch, Tavily calls).
- **Graceful degradation**: Missing keys or optional libs do not crash the app; features disable individually with clear log warnings.

---

## 🗺️ Roadmap

- Real‑time streaming TTS with smooth cross‑fade
- On‑device VAD tuning and sensitivity slider
- Multi‑voice profiles and style tags (cheerful, narrator, whisper)
- Rich cards (links, images, citations) in chat bubbles
- Persistent session storage and multi‑device sync

---

## 📄 License

All Rights Reserved

Copyright (c) 2025 Bipul Shukla

This source code and its contents are the exclusive property of Bipul Shukla.
Unauthorized use, copying, modification, merging, publishing, distribution, sublicensing, 
or sale of this code or any derivative works is strictly prohibited.

You may not:
- Use this code for any purpose without prior written permission.
- Copy, modify, merge, publish, distribute, sublicense, or sell copies of the code.
- Create derivative works from this code.

For inquiries regarding usage rights, please contact: iambipulshukla@gmail.com .
Check the licenses and usage limits for APIs before deploying to production.




