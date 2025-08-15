# AI Voice Agent

A modern, browser‑based voice assistant built with FastAPI and a rich, animated UI. AVA lets you:
- Speak to the assistant and get transcribed text using AssemblyAI
- Get AI responses powered by Google Gemini, with session‑aware conversation history
- Hear the assistant’s response as natural speech generated via Murf AI
- Use a text‑only chat flow when voice isn’t available

The frontend is a single, responsive HTML page with a polished gradient UI and animated avatar, and the backend exposes a clean set of JSON APIs.

---

## Acknowledgement

This project was developed with support from [Murf AI] (https://murf.ai).

---

## Table of Contents
1. Features
2. Architecture Overview
3. Tech Stack
4. Project Structure
5. Environment Variables
6. Running Locally
7. API Reference
8. Frontend UX Notes
9. Testing
10. Deployment Notes

---

## 1) Features
- Conversational voice chat (record → transcribe → AI → TTS return)
- Session‑aware chat memory per `session_id`
- Text‑only chat endpoint for quick testing and accessibility
- Echo Bot demo (transcribe your voice and speak it back using TTS)
- Clean, animated UI with mobile‑friendly layout
- PWA manifest and favicon for an app‑like feel

---

## 2) Architecture Overview

High‑level flow (Voice Chat):
1. Browser records microphone audio (Web MediaRecorder).
2. Frontend sends audio to the backend `/llm/query` with a `session_id`.
3. Backend transcribes speech via AssemblyAI.
4. Backend calls Google Gemini with ongoing chat history for the session.
5. Backend sends AI text to Murf AI to generate a voice reply (MP3).
6. Frontend displays both text and an audio player for the reply.

Text‑only flow:
- Frontend (or script) sends text + `session_id` to `/llm/text-query`.
- Backend calls Gemini and returns the AI text (updates session history).

Session management:
- In‑memory `chat_sessions` dictionary on the server keyed by `session_id`.
- `/chat/clear` clears a session’s stored history.

---

## 3) Tech Stack
- **Backend**: FastAPI, Uvicorn
- **AI APIs**:
  - **AssemblyAI**: Speech‑to‑Text
  - **Google Gemini**: Text generation (chat)
  - **Murf AI**: Text‑to‑Speech
- **Frontend**: Vanilla HTML/CSS/JS, Font Awesome, Google Fonts
- **PWA**: `static/manifest.json` with inline SVG icons

---

## 4) Project Structure
```
AVA/
├─ main.py                 # FastAPI app, routes, integrations
├─ templates/
│  └─ index.html           # Single‑page UI (Jinja served)
├─ static/
│  ├─ script.js            # Frontend logic (tabs, recording, chat)
│  └─ manifest.json        # PWA manifest & icons
├─ uploads/
│  └─ .env                 # Local environment variables (not for production)
├─ test_ai_chat.py         # Quick API test script for text chat
└─ README.md               # You are here
```

---

## 5) Environment Variables
Create `uploads/.env` with:
- **MURF_API_KEY**: Murf AI API key (required for TTS)
- **ASSEMBLYAI_API_KEY**: AssemblyAI API key (required for transcription)
- **GEMINI_API_KEY**: Google Generative AI API key (required for LLM)

Example `uploads/.env`:
```
MURF_API_KEY=your_murf_key
ASSEMBLYAI_API_KEY=your_assemblyai_key
GEMINI_API_KEY=your_gemini_key
```

Notes:
- Keys are loaded via `dotenv` in `main.py` using `load_dotenv("uploads/.env")`.
- If a key is missing, the app continues to run and returns a graceful fallback with a local placeholder MP3 for TTS endpoints.

---

## 6) Running Locally

Prerequisites:
- Python 3.10+
- API keys for AssemblyAI, Gemini, and Murf AI

Steps:
1. Create and activate a virtual environment (recommended).
2. Install dependencies.
3. Add `uploads/.env` with your keys.
4. Start the API server.
5. Open the UI in your browser.

Example commands:
```powershell
# 1) (Windows PowerShell) create venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) install dependencies
pip install fastapi uvicorn python-dotenv requests assemblyai google-generativeai

# 3) ensure .env exists with your keys in uploads/.env
# (see Environment Variables section)

# 4) run server
python main.py
# Server will start at http://localhost:8000
```

---

## 7) API Reference

Base URL: `http://localhost:8000`

- **GET /**
  - Serves the main UI (`templates/index.html`).

- **POST /generate-audio/**
  - Body (JSON): `{ "text": string }`
  - Returns: `{ audioFile, ... }` — Murf AI TTS; falls back to `static/fallback.mp3` if key missing.

- **POST /tts/echo/**
  - Form‑Data: `file` (audio upload)
  - Transcribes audio using AssemblyAI and regenerates speech with Murf AI.
  - Returns JSON with `audioFile` and `transcription`.

- **POST /llm/query**
  - Form‑Data: `file` (audio upload), `session_id` (string)
  - Pipeline: STT → Gemini → TTS
  - Returns JSON with `userTranscription`, `llmResponse`, `audioFile`.

- **POST /llm/text-query**
  - Body (JSON): `{ "text": string, "session_id": string }`
  - Sends text to Gemini with session history.
  - Returns: `{ llmResponse: string }`.

- **POST /chat/clear**
  - Body (JSON): `{ "session_id": string }`
  - Clears in‑memory history for a session.

HTTP error handling:
- Endpoints return descriptive JSON errors and `fallback: true` if any external API key is missing or errors occur.

---

## 8) Frontend UX Notes
- UI delivers a modern animated experience with: floating particles, glowing orbs, animated waves, and a breathing avatar.
- Voice chat controls include start/stop recording, auto‑record toggle, text‑only toggle, and history clear.
- Chat bubbles use high‑contrast text colors for readability.
- Mobile‑optimized: compact session/info badges left‑aligned on small screens.

PWA:
- `static/manifest.json` defines name, theme, and icons (valid inline SVGs).
- Add to home screen is supported by modern browsers.

---

## 9) Testing
Quick text‑chat tests:
```bash
python test_ai_chat.py
```
- Hits `/llm/text-query` and `/chat/clear` to verify conversation continuity and clearing.
- Make sure the server is running at `http://localhost:8000` before executing the test script.

---

## 10) Deployment Notes
- Set environment variables securely in your hosting platform; do not commit `.env` files.
- Behind a reverse proxy, set CORS and `allow_origins` appropriately in `main.py`.
- Run with a production server command, for example:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```
- Persisting chat history: current implementation stores sessions in memory; for multi‑instance or long‑lived sessions, use a database or cache (Redis) and adapt the `chat_sessions` store.

---

## Diagram — Voice Conversation Flow
```
[Browser Mic]
    │  audio
    ▼
POST /llm/query (file + session_id)
    │
    ├─> AssemblyAI (STT)
    │      └─ userTranscription
    │
    ├─> Google Gemini (chat with history)
    │      └─ llmResponse text
    │
    └─> Murf AI (TTS)
           └─ audioFile (MP3 URL)

Response → { userTranscription, llmResponse, audioFile }
UI → Show text, update chat bubbles, play audio
```

---

## License

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
Check the licenses and usage limits for AssemblyAI, Google Generative AI, and Murf AI before deploying to production.


