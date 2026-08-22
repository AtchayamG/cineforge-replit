# Submission Evidence Matrix — Replit Track

| Official requirement | Evidence | Status | Truthful note |
|---|---|---:|---|
| Functional web app | `backend/app/main.py`, `backend/app/static/index.html`; https://cineforge-replit--atchayamganesh.replit.app | PASS | Public UI, API workflow, snapshot retrieval, and health endpoint verified. |
| Google AI used at runtime | `backend/app/services/gemini_service.py` | IMPLEMENTED | Official `google-genai` call to `gemini-2.5-flash`; authenticated smoke evidence must be recorded separately. |
| Built using Replit Agent | `docs/assets/replit-agent-evidence.jpg`; pushed commits `9dd513a` and `163d7d4` | PASS | Replit Agent added the snapshot retrieval endpoint/UI/tests and recorded an authentic checkpoint; a later independent hardening pass expanded the suite to 14 tests. |
| Hosted directly on Replit | https://cineforge-replit--atchayamganesh.replit.app; `docs/assets/replit-published-app.jpg` | PASS | Public deployment was verified outside the editor; `/api/v1/health` reports Replit runtime, published state, public URL, and demo mode. |
| Replit runtime integration | `.replit`, `replit.nix`, `replit_environment_service.py` | PASS (CODE) | Reads `REPLIT_DOMAINS`, `REPLIT_DEV_DOMAIN`, and `REPLIT_DEPLOYMENT`; no fabricated cloud state. |
| Honest live/demo separation | `config.py`, `gemini_service.py`, judge UI | PASS | Demo fixtures are labeled. Live failures do not silently become demo output by default. |
| Public open-source repository | https://github.com/AtchayamG/cineforge-replit + root `LICENSE` | PASS | Public repository with an OSI-approved MIT license at repository root. |
| Public video under three minutes | `docs/VIDEO_DEMO_SCRIPT.md`; public YouTube URL pending | READY | Final 1920x1080 video is 172.1 seconds with Sonia narration, burned-in captions, and a custom thumbnail; public publishing is the remaining step. |
| Automated verification | `python -m pytest -q` | PASS | 14 tests pass, including runtime-mode labeling, bounded snapshot retention, CORS safety, snapshot retrieval, and missing-ID behavior. |

## Claims intentionally removed

- No claim of three live collaborators or multiplayer presence.
- No claim that the application creates Replit branches.
- No invented `.replit.app` preview links; the documented URL is the verified public deployment.
- No fixed “under five seconds” startup claim without measurement.
- Review snapshots are explicitly in-memory and reset with the process.
