# ⚡ CineForge Replit: Cloud Cinema Review Sandbox

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Track](https://img.shields.io/badge/Track-Replit_Partner_Track-orange.svg)](https://agentic-cinema.devpost.com)
[![Google Gemini](https://img.shields.io/badge/AI-Google_Gemini_2.5_Flash-cyan.svg)](https://ai.google.dev)
[![Replit](https://img.shields.io/badge/Replit-1--Click_Deploy-red.svg)](https://replit.com)

> **CineForge Replit** turns a scene draft and a director note into an inspectable dialogue, camera, lighting, sound, and VFX review packet in one browser session, powered by **Replit** and **Google Gemini 3.7 Flash**.

**Live judge app:** https://cineforge-replit--atchayamganesh.replit.app

---

## 🌟 Key Capabilities
- **⚡ Replit-Native Execution**: `.replit` and `replit.nix` define the reproducible run environment; the submitted evaluator is published directly on Replit.
- **🤖 Gemini 3.7 Co-Director**: The Google GenAI SDK refines dialogue and produces camera, lighting, sound, and visual-staging guidance.
- **🎬 Review Snapshots**: Each run creates an explicitly in-memory review snapshot; no source-control branch or durable collaboration feature is implied.
- **🛡️ Honest Mode Separation**: Transparently switches between live Google Gemini calls and deterministic demo fixtures with verifiable evidence source metadata.

---

## 🚀 Quickstart

### Option A: Run on Replit (1-Click)
1. Fork or import this repository into Replit.
2. Click the green **"Run"** button.
3. Replit installs the declared dependencies and launches the studio on its assigned public port.

### Option B: Run Locally
```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch server
python run_backend.py

# 4. Open browser
http://localhost:8004/
```

---

## 🧪 Testing & Verification
```bash
cd backend
python -m pytest -v
# Verified: 30 tests passing.
```

---

## 📚 Project Documentation
- [Architecture Whitepaper](docs/ARCHITECTURE.md)
- [Devpost Submission Narrative](docs/DEVPOST_SUBMISSION.md)
- [Submission Evidence Matrix](docs/SUBMISSION_EVIDENCE.md)
- [3-Minute Demo Video Script](docs/VIDEO_DEMO_SCRIPT.md)
- [Codex Verification Handoff](docs/AGY_HANDOFF.md)
