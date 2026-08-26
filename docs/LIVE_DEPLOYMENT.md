# Live Deployment & Gemini Runtime Guide — CineForge Replit (Track 5)

## Overview

CineForge Replit operates in two distinct operational dimensions:
1. **Authentic Replit Container Environment**: Auto-detected via Replit container telemetry (`REPL_ID`, `REPL_SLUG`, `REPLIT_DOMAINS`, `REPLIT_DEV_DOMAIN`, `REPLIT_DEPLOYMENT`).
2. **Google Gemini 3.7 Runtime Mode**: Controlled via `GEMINI_RUNTIME_MODE` (or fallback `RUNTIME_MODE`) using the official `google-genai` SDK with `gemini-3.7-flash`.

These dimensions are completely independent: running in a Replit container does not imply live Gemini credentials are present, and local development can independently test live or demo execution paths.

---

## Configuration & Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `GEMINI_RUNTIME_MODE` | `""` (falls back to `RUNTIME_MODE`) | Controls Gemini execution: `live` for live Gemini 3.7 Flash calls, `demo` for deterministic scene fixtures. |
| `RUNTIME_MODE` | `"demo"` | Legacy runtime mode setting; sets default for `GEMINI_RUNTIME_MODE` for backwards compatibility. |
| `GEMINI_API_KEY` | `""` | Google AI Studio API key (configured in Replit Secrets; never checked into source control). |
| `GEMINI_RELAY_URL` | `""` | Optional Cloud Run relay URL used when Replit should reach Vertex AI without a service-account key. |
| `GEMINI_RELAY_TOKEN` | `""` | Shared relay credential stored only in Replit Secrets and the Cloud Run service environment. |
| `GEMINI_MODEL` | `"gemini-3.7-flash"` | Gemini model identifier for co-direction and visual staging compilation. |
| `GOOGLE_CLOUD_PROJECT` | `""` | Optional Google Cloud project ID for Vertex AI execution. |
| `GOOGLE_CLOUD_LOCATION` | `"global"` | Vertex AI region (Gemini 3.7 Flash defaults to `global`). |

---

## Replit Secrets Setup for Genuine Live Gemini 3.7 Calls

To enable live Gemini 3.7 Flash generation on Replit:

1. Open the CineForge Replit project in your Replit workspace.
2. In the left-hand sidebar, open **Tools > Secrets** (or the Environment Variables pane).
3. Add the following Secrets:
   - **Key**: `GEMINI_API_KEY`  
     **Value**: Your valid Google AI Studio Gemini API key.
   - **Key**: `GEMINI_RUNTIME_MODE`  
     **Value**: `live`
4. Restart the Replit container or click the green **Run** button.

### Truthfulness & Zero-Secret Guarantee
- **No secrets or credentials are baked into the repository, git history, or published assets.**
- **Never claim a secret or live call exists** unless genuinely configured in the host environment.
- In the public sandbox or default checkout where no `GEMINI_API_KEY` is configured, `GEMINI_RUNTIME_MODE` defaults to `demo`, executing deterministic screenplay co-direction fixtures with explicit metadata.

---

## Fail-Closed Behavior (No Silent Fallback)

In live mode (`GEMINI_RUNTIME_MODE=live`), the system enforces strict **fail-closed** semantics:

- **Missing Credentials**: If `GEMINI_RUNTIME_MODE=live` is configured but neither `GEMINI_API_KEY` nor Vertex AI credentials are present, `GeminiService` immediately returns:
  - `success: False`
  - `mode: "live_error"`
  - `error: "Live Gemini mode requested but Gemini client is uninitialized (missing API key or Vertex credentials)."`
- **API Exceptions**: If the live Google GenAI API call raises an exception (e.g. rate limit, invalid key, or network failure), `GeminiService` returns `success: False` and `mode: "live_error"`.
- **No Silent Fixture Fallback**: Live execution will **never** silently fall back to demo fixtures. The UI mode badge truthfully transitions to `MODE: LIVE ERROR` (`#ef4444`) so judges and operators always know the exact runtime state.

---

## Health Endpoint & Runtime Verification

The health check endpoint at `/api/v1/health` reports Gemini configuration, active mode, and authentication evidence separately from authentic Replit container telemetry:

```json
{
  "status": "healthy",
  "service": "CineForge Replit",
  "track": "Replit Partner Track",
  "runtime_mode": "demo",
  "gemini_runtime_mode": "demo",
  "providers": {
    "google_gemini": {
      "mode": "demo",
      "configured": false,
      "auth_type": "none",
      "auth_evidence": "No Gemini credentials configured",
      "model": "gemini-3.7-flash"
    },
    "replit_environment": {
      "detected": false,
      "repl_slug": "local",
      "published": false,
      "public_url": null
    }
  }
}
```

- When configured with `GEMINI_API_KEY`, `auth_type` reports `"api_key"` and `auth_evidence` reports `"GEMINI_API_KEY environment variable present"` without ever revealing the secret key.
- When hosted in Replit Cloud, `replit_environment.detected` becomes `true`, `repl_slug` reflects the authentic container slug, and `public_url` reflects the authentic `.replit.app` deployment URL.

---

## Cloud Run Vertex Relay

For keyless Replit-to-Vertex execution, the repository includes a minimal relay path:

- The same backend can be deployed to **Google Cloud Run** with Vertex AI enabled.
- The Cloud Run service would authenticate to Vertex AI using Google Cloud Workload Identity / Application Default Credentials (ADC) to invoke `gemini-3.7-flash` in location `global`.
- Replit calls `/api/v1/forge/relay/collaborate` over HTTPS with `GEMINI_RELAY_TOKEN`; the endpoint uses constant-time token comparison and is unavailable when no token is configured.
- Replit stores only the narrow relay token, not a Google service-account JSON key. The Cloud Run runtime identity remains the only principal allowed to call Vertex AI.
- Set `GEMINI_RELAY_URL`, `GEMINI_RELAY_TOKEN`, and `GEMINI_RUNTIME_MODE=live` in Replit. Remove `GEMINI_API_KEY` so the health endpoint reports `auth_type: cloud_run_relay`.

Cloud Run must set `GEMINI_RELAY_TOKEN`, `GEMINI_RUNTIME_MODE=live`, `GOOGLE_CLOUD_PROJECT=atlas-495807`, `GOOGLE_CLOUD_LOCATION=global`, and `GEMINI_MODEL=gemini-3.7-flash`. It must not set `GEMINI_RELAY_URL`; this prevents relay recursion. With this receiver configuration, the ordinary `/api/v1/forge/collaborate` route is disabled and only the token-protected relay endpoint can invoke Vertex AI.

The relay is configuration evidence until a real public `/api/v1/forge/collaborate` request returns `runtime_mode: live`; health metadata alone is never presented as proof of successful inference.

---

## Local Verification Commands

To verify all runtime modes and fail-closed behaviors locally:

```bash
cd backend
python -m pytest -v
```
