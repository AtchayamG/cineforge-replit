# 🤖 Agent Handoff Document: Track 5 (Replit Track)

## Project: CineForge Replit
**Workspace Path:** `D:\Work\Gemini\Hackathon\Agentic Cinema\Track5_Replit_CineForge`

---

## 1. System Summary
- **Track:** Replit Partner Track
- **Runtime Port:** 8004
- **Core Technology:** Replit runtime + Google Gemini 2.5 Flash (`google-genai` SDK) + FastAPI
- **Web UI Location:** `http://localhost:8004/` (served from `backend/app/static/index.html`)

---

## 2. Key Modules
- `.replit` & `replit.nix`: 1-Click execution configuration for Replit Cloud.
- `backend/app/services/gemini_service.py`: Google GenAI integration for collaborative co-direction.
- `backend/app/services/replit_environment_service.py`: Replit runtime evidence and in-session review snapshots.
- `backend/app/agents/codirector_agent.py`: Multi-agent co-direction coordinator.
- `backend/app/main.py`: FastAPI server with static UI mounting and health endpoint.
- `backend/tests/test_replit_forge.py`: 100% passing test suite.

---

## 3. Verification Commands
```bash
# Run test suite
cd "Track5_Replit_CineForge\backend"
python -m pytest -q
# Run the command to obtain the current count.
```
