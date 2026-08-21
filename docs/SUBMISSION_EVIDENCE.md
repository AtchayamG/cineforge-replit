# Submission Evidence Matrix — Replit Track

| Official requirement | Evidence | Status | Truthful note |
|---|---|---:|---|
| Functional web app | `backend/app/main.py`, `backend/app/static/index.html` | PASS | Local UI, API workflow, and health endpoint verified. |
| Google AI used at runtime | `backend/app/services/gemini_service.py` | IMPLEMENTED | Official `google-genai` call to `gemini-2.5-flash`; authenticated smoke evidence must be recorded separately. |
| Built using Replit Agent | Replit Agent chat/checkpoint screenshot | BLOCKED | Mandatory partner evidence; local files alone cannot prove Replit Agent usage. |
| Hosted directly on Replit | Public `.replit.app` URL and `/api/v1/health` response | BLOCKED | Mandatory; must be published and verified outside the editor. |
| Replit runtime integration | `.replit`, `replit.nix`, `replit_environment_service.py` | PASS (CODE) | Reads `REPLIT_DOMAINS`, `REPLIT_DEV_DOMAIN`, and `REPLIT_DEPLOYMENT`; no fabricated cloud state. |
| Honest live/demo separation | `config.py`, `gemini_service.py`, judge UI | PASS | Demo fixtures are labeled. Live failures do not silently become demo output by default. |
| Public open-source repository | https://github.com/AtchayamG/cineforge-replit + root `LICENSE` | PASS | Public repository with an OSI-approved MIT license at repository root. |
| Public video under three minutes | Public YouTube URL | BLOCKED | Final video and custom thumbnail are pending. |
| Automated verification | `python -m pytest -q` | PASS | 7 tests pass after the truthfulness audit. |

## Claims intentionally removed

- No claim of three live collaborators or multiplayer presence.
- No claim that the application creates Replit branches.
- No invented `.replit.app` preview links.
- No fixed “under five seconds” startup claim without measurement.
- Review snapshots are explicitly in-memory and reset with the process.
