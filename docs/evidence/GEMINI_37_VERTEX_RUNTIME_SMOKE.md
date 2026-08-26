# Gemini 3.7 Vertex AI Runtime Smoke

- Verified: 2026-08-25 (Asia/Calcutta)
- Google Cloud project: `atlas-495807`
- API: Vertex AI (`aiplatform.googleapis.com`)
- Model: `gemini-3.7-flash`
- Location: `global`
- Result: HTTP 200 with the expected `MODEL_OK` marker
- Negative control: the equivalent `us-central1` request returned HTTP 404 `NOT_FOUND`

The smoke used the active Google Cloud CLI identity and a short-lived access token without printing or storing that token. It proves authenticated model availability in `global`. It does not prove that the public Replit deployment is configured for live mode.
