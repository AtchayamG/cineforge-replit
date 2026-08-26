# Submission Evidence Matrix — Replit Track

| Official requirement | Evidence | Status | Truthful note |
|---|---|---:|---|
| Functional web app | `backend/app/main.py`, `backend/app/static/index.html`; https://cineforge-replit--atchayamganesh.replit.app | PASS | Public UI, API workflow, snapshot retrieval, and health endpoint verified. |
| Google AI used at runtime | `backend/app/services/gemini_service.py`; `docs/evidence/GEMINI_37_VERTEX_RUNTIME_SMOKE.md`; public `/api/v1/health` and `/api/v1/forge/collaborate` | PASS (PUBLIC LIVE RUNTIME) | The public Replit app calls `gemini-3.7-flash` through an authenticated Cloud Run relay and Vertex AI. A public collaboration request returned a real structured review packet with `runtime_mode: live` and explicit Vertex evidence. |
| Built using Replit Agent | `docs/assets/replit-agent-evidence.jpg`; pushed commits `9dd513a` and `163d7d4` | PASS | Replit Agent added the snapshot retrieval endpoint/UI/tests and recorded an authentic checkpoint; a later independent hardening pass expanded the suite to 30 tests. |
| Hosted directly on Replit | https://cineforge-replit--atchayamganesh.replit.app; `docs/assets/replit-published-app.jpg` | PASS | Public deployment was verified outside the editor. `/api/v1/health` reports Replit runtime, published state, `live` Gemini mode, `cloud_run_relay` authentication, and `gemini-3.7-flash`. |
| Replit runtime integration | `.replit`, `replit.nix`, `replit_environment_service.py` | PASS (CODE) | Reads `REPLIT_DOMAINS`, `REPLIT_DEV_DOMAIN`, and `REPLIT_DEPLOYMENT`; no fabricated cloud state. |
| Honest live/demo separation | `config.py`, `gemini_service.py`, judge UI | PASS | Demo fixtures are labeled. Live failures do not silently become demo output by default. |
| Public open-source repository | https://github.com/AtchayamG/cineforge-replit + root `LICENSE` | PASS | Public repository with an OSI-approved MIT license at repository root. |
| Public video under three minutes | https://youtu.be/7SPam_1jiV4; `docs/VIDEO_DEMO_SCRIPT.md` | PASS | The final 2:53 Gemini 3.7 edition is public at 1920x1080 with Sonia narration, burned-in English captions, and a custom thumbnail. |
| Automated verification | `python -m pytest -q` | PASS | 30 tests pass, including runtime-mode labeling, relay authentication and failure handling, bounded snapshot retention, CORS safety, snapshot retrieval, and missing-ID behavior. |

## Claims intentionally removed

- No claim of three live collaborators or multiplayer presence.
- No claim that the application creates Replit branches.
- No invented `.replit.app` preview links; the documented URL is the verified public deployment.
- No fixed “under five seconds” startup claim without measurement.
- Review snapshots are explicitly in-memory and reset with the process.
