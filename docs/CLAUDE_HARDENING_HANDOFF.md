# Claude Hardening Handoff — Track 5 CineForge Replit

**Branch:** `agent/track5-claude-hardening`
**Base commit:** `163d7d4`
**Code commit:** `be7aead14c80afa69d1d382ee5360d34de9c0a10` (`be7aead`)
**Date:** 2026-08-22

---

## Result

All six required code-level changes are implemented and the full backend pytest suite
passes (14 passed, up from a 9-passed baseline). No product scope changed, no
credentials or evidence were fabricated, and no submission docs were edited.

---

## Files changed

| File | Change |
| --- | --- |
| `backend/app/static/index.html` | MODE badge no longer carries a static claim. Ships as `MODE: CHECKING RUNTIME` and is set only from backend runtime evidence. |
| `backend/app/agents/codirector_agent.py` | Collaborate response now returns `runtime_mode` — the mode that actually executed — on both the success and `LIVE_ERROR` paths. |
| `backend/app/main.py` | CORS no longer sets `allow_credentials=True` alongside a wildcard origin; wildcard now sourced from the previously unused `settings.CORS_ORIGINS`. |
| `backend/app/services/replit_environment_service.py` | Snapshot store is a bounded FIFO (`OrderedDict`, `MAX_REVIEW_SNAPSHOTS = 50`) with oldest-first eviction; cap surfaced as `review_snapshots_max` and per-snapshot `retention`. |
| `backend/app/config.py` | `REPL_SLUG` defaults to `""` instead of `"cineforge-replit-studio"`. |
| `.env.example` | `REPL_SLUG=` left empty with a comment that Replit populates it. |
| `backend/app/services/gemini_service.py` | `imagen3_vfx_prompt` renamed to `vfx_image_prompt` in both the request schema and the demo fixture. |
| `.replit` | `modules` pinned to `python-3.11` to match `replit.nix` and the docs. |
| `backend/tests/test_replit_forge.py` | Five new regression tests plus field-name assertions on the existing Gemini test. |

---

## Change detail

### 1. MODE badge derives from real backend runtime evidence

The badge previously read `MODE: DEMO FIXTURES` as hardcoded markup, so it would have
stayed stale had the deployment ever run with `RUNTIME_MODE=live`.

Now:

- The span ships as `MODE: CHECKING RUNTIME` with neutral styling — the page asserts nothing.
- `loadModeBadge()` reads `/api/v1/health.runtime_mode` on page load.
- After each run, `applyModeBadge(data.runtime_mode)` corrects the badge from the
  collaborate response.

The two sources can legitimately disagree, and the collaborate value is the more
truthful one: `health.runtime_mode` reports the **configured** mode, while the
collaborate value reports the mode that **actually executed**. If `RUNTIME_MODE=live`
were ever set but no Gemini client could be initialized, `GeminiService` falls through
to the demo fixture and reports `mode: "demo"` — the badge follows the real execution
path, not the config. `live_error` renders as `MODE: LIVE ERROR`; an unreachable or
malformed health response renders `MODE: UNAVAILABLE` rather than guessing.

Regression test: `test_mode_badge_is_derived_from_backend_runtime_evidence` asserts the
served markup's badge text is exactly `MODE: CHECKING RUNTIME` and that the wiring to
`/api/v1/health`, `health.runtime_mode`, and `applyModeBadge(data.runtime_mode)` is
present — so re-hardcoding a mode claim fails the suite.
`test_health_and_collaborate_report_the_same_runtime_mode` asserts the two endpoints
agree (and are both `demo`) when no Gemini credentials are configured.

### 2. Credentialed wildcard CORS removed

`allow_origins=["*"]` with `allow_credentials=True` is the classic misconfiguration.
Nothing in this app uses cookies, sessions, or an `Authorization` header, so there was
no requirement to satisfy — and browsers reject that combination regardless. Dropped to
`allow_credentials=False`. The wildcard origin is retained so the public demo stays
usable from any judge's browser, now read from `settings.CORS_ORIGINS`, which existed
but was being ignored in favour of an inline literal.

Test: `test_cors_is_not_credentialed_with_a_wildcard_origin` asserts
`access-control-allow-origin: *` is still present and
`access-control-allow-credentials` is absent.

### 3. Snapshot collection bounded

`/api/v1/forge/stage` and `/api/v1/forge/collaborate` are both unauthenticated and both
insert into `review_snapshots`, which was an unbounded dict — repeated public requests
grew process memory without limit for the life of the container.

Now an `OrderedDict` capped at `MAX_REVIEW_SNAPSHOTS = 50` with oldest-first eviction.
50 is far more than a judging session needs while keeping the retained payload trivial.
The bound is documented in three places so it is not a silent behaviour change: a
comment at the constant, `review_snapshots_max` in the environment status payload, and a
`retention` field on every snapshot returned.

Test: `test_review_snapshots_are_bounded` creates `cap + 5` snapshots and asserts the
store holds exactly `cap`, the first-created snapshot is gone, the last is retained, and
the reported cap matches. It saves and restores the shared singleton's store so it does
not perturb the other tests.

### 4. Truthful off-Replit `REPL_SLUG`

The default was `"cineforge-replit-studio"` — a plausible-looking hosted slug reported
by `/api/v1/health` and `/forge/replit/environment` even when running on a laptop with
no Replit container anywhere in the picture. Default is now `""`, and
`get_replit_status()` already rendered an empty slug as `"local"`, so the local answer is
now honestly `local`.

Test: `test_repl_slug_is_not_fabricated_off_replit`.

### 5. Python version aligned

Three sources disagreed: `.replit` declared `python-3.12`, `replit.nix` pinned
`python311*`, and `docs/DEVPOST_SUBMISSION.md` states Python 3.11.

Aligned on **3.11** by changing `.replit` only. That was the one-line fix that makes all
sources agree without touching submission docs (off-limits per the brief) and without
touching `replit.nix`. It is also the version the suite actually runs on here
(Python 3.11.15), so the declared version now matches verified reality.

No install-on-every-run step was added. See Risks for the pre-existing one.

### 6. `imagen3_vfx_prompt` renamed

Renamed to `vfx_image_prompt` in the Gemini request schema and the demo fixture. The
field is and always was a **text prompt string** produced by Gemini 2.5 Flash; no Imagen
3 call is made anywhere in the codebase, so the old name implied a model integration that
does not exist.

No API compatibility shim was added: the field is nested inside
`gemini_collaboration` in the response, the UI never rendered it, and no test or doc
referenced the old key (verified by grep). An alias would have preserved exactly the
misleading name this change exists to remove.

Test: the existing `test_gemini_collaborative_co_direction` now asserts
`vfx_image_prompt` is present and `imagen3_vfx_prompt` is absent.

---

## Tests run

Command, from `backend/`:

```
python -m pytest -v
```

Environment: Python 3.11.15, pytest 9.1.1, pytest-asyncio 1.4.0 (strict mode), win32.

**Outcome: `14 passed in 0.40s`.** Zero failures, zero errors, zero skips, zero warnings.
Baseline before this work was `9 passed in 0.42s`.

Full list — all 14 PASSED:

```
tests/test_replit_forge.py::test_replit_environment_status                           PASSED
tests/test_replit_forge.py::test_gemini_collaborative_co_direction                   PASSED
tests/test_replit_forge.py::test_replit_review_snapshot                              PASSED
tests/test_replit_forge.py::test_review_snapshot_can_be_retrieved_by_id              PASSED
tests/test_replit_forge.py::test_missing_review_snapshot_returns_not_found           PASSED
tests/test_replit_forge.py::test_codirector_agent_end_to_end                         PASSED
tests/test_replit_forge.py::test_health_endpoint_is_explicit_about_runtime           PASSED
tests/test_replit_forge.py::test_judge_ui_uses_truthful_snapshot_language            PASSED
tests/test_replit_forge.py::test_local_runtime_does_not_invent_public_url            PASSED
tests/test_replit_forge.py::test_mode_badge_is_derived_from_backend_runtime_evidence PASSED
tests/test_replit_forge.py::test_health_and_collaborate_report_the_same_runtime_mode PASSED
tests/test_replit_forge.py::test_cors_is_not_credentialed_with_a_wildcard_origin     PASSED
tests/test_replit_forge.py::test_review_snapshots_are_bounded                        PASSED
tests/test_replit_forge.py::test_repl_slug_is_not_fabricated_off_replit              PASSED
```

Five tests are new; the other nine are the pre-existing suite, unchanged except for the
two added field assertions inside `test_gemini_collaborative_co_direction`.

---

## Assumptions

1. **3.11 is the right alignment target, not 3.12.** Chosen because `replit.nix` and
   `docs/DEVPOST_SUBMISSION.md` already said 3.11 and docs were off-limits — so a
   one-line `.replit` change reconciles everything. If the intent was 3.12, revert
   `.replit` and update `replit.nix` plus the doc instead.
2. **No API-compatibility shim is needed for the renamed field.** Based on a grep showing
   no remaining `imagen3_vfx_prompt` reference in code, tests, UI, or docs.
3. **A cap of 50 snapshots is generous for judging.** It is a single class constant if
   that turns out to be wrong.
4. **Wildcard CORS should stay.** The brief said to keep the public demo functional and
   there is no auth to protect; only the `credentials` flag was the defect.
5. **The badge should prefer the executed mode over the configured mode** when they
   disagree. This is the interpretation that cannot produce a false LIVE claim.
6. **Static-HTML assertions are an acceptable regression test for the badge.** There is
   no JS test runner in this repo and adding one would exceed the brief's "minimal and
   reviewable" constraint. The tests pin the served markup and the wiring, which is what
   would regress.

---

## Risks

1. **The badge tests are string-matching assertions against `index.html`.** They will
   break on an innocuous refactor of the JS (for example renaming `applyModeBadge`). That
   is a deliberate trade for having any regression guard at all without a JS test runner —
   a future editor should update the assertions rather than delete them.
2. **`.replit` `modules = ["python-3.11"]` is not verified on Replit from here.** The
   change is a declaration; it has not been exercised in a real Replit container in this
   session. Worth a smoke run of the Run button before submission.
3. **A pre-existing install-on-every-run step remains in `.replit`:** the workflow task is
   `cd backend && pip install -r requirements.txt && python run_backend.py`. The brief
   said not to *add* one, so it was left alone — removing it risks breaking the judge's
   one-click Run, since nothing else in `.replit` installs dependencies. Flagged as a
   known fragility rather than silently changed.
4. **The snapshot cap is per-process, not per-client.** A single client can still evict
   another client's snapshot by making 50 requests. Acceptable for a demo with no auth and
   explicitly session-local, restart-volatile snapshots; it is not a multi-tenant-safe
   design and should not be described as one.
5. **`runtime_mode` is a new key in the collaborate response.** Additive only, so no
   existing consumer breaks, but any doc that enumerates that response's fields is now
   incomplete.
6. **Unverified in a live browser.** All verification was via FastAPI's `TestClient`; the
   JS badge path was not executed in a real browser in this session.
7. **Docs still reference the old numbers in places** — for example any test count in
   `docs/SUBMISSION_EVIDENCE.md` is now 14, not 9. Docs were out of scope per the brief;
   the primary agent should reconcile the count and any mention of the renamed field.

---

## Not done

- No credentials, secrets, API keys, or screenshots were added.
- `RUNTIME_MODE` remains `demo`; no live Gemini execution is claimed anywhere.
- No submission docs were edited.
