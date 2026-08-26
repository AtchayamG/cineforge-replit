import re

import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.services.gemini_service import gemini_service
from app.services.replit_environment_service import replit_service
from app.agents.codirector_agent import codirector_agent
from app.main import app

@pytest.mark.asyncio
async def test_replit_environment_status():
    status = replit_service.get_replit_status()
    assert "repl_slug" in status
    assert status["one_click_run_status"] in {"RUNNING_ON_REPLIT", "CONFIG_PRESENT_NOT_CLOUD_VERIFIED"}
    assert status["runtime_evidence"] in {"Replit predefined environment variables", "Local runtime inspection"}
    assert "review_snapshots_active" in status

@pytest.mark.asyncio
async def test_gemini_collaborative_co_direction():
    res = gemini_service.collaborate_on_scene(
        scene_title="Scene 1: Atmospheric Breach",
        working_script="EXT. NEO-TOKYO RUNWAY - NIGHT",
        director_instruction="Add 35mm anamorphic camera cues"
    )
    assert res["success"] is True
    assert "data" in res
    assert "dialogue_refinements" in res["data"]
    assert "camera_staging" in res["data"]
    assert "vfx_image_prompt" in res["data"]
    assert "imagen3_vfx_prompt" not in res["data"]

@pytest.mark.asyncio
async def test_replit_review_snapshot():
    res = replit_service.stage_scene_branch("room-alpha", "Scene 1", "Script Draft")
    assert res["status"] == "REVIEW_SNAPSHOT_CREATED"
    assert res["snapshot_id"].startswith("review-")
    assert res["persistence"] == "in_memory_until_restart"
    if res["review_url"]:
        assert res["review_url"].startswith("https://")

def test_review_snapshot_can_be_retrieved_by_id():
    created = replit_service.stage_scene_branch("room-retrieval", "Scene Retrieval", "Script Draft")
    response = TestClient(app).get(f"/api/v1/forge/snapshots/{created['snapshot_id']}")
    assert response.status_code == 200
    assert response.json() == created

def test_missing_review_snapshot_returns_not_found():
    response = TestClient(app).get("/api/v1/forge/snapshots/review-does-not-exist")
    assert response.status_code == 404
    assert "current app session" in response.json()["detail"]

@pytest.mark.asyncio
async def test_codirector_agent_end_to_end():
    res = await codirector_agent.collaborate_and_stage(
        scene_title="Scene 1: Sector 9",
        working_script="EXT. NEO-TOKYO - NIGHT",
        director_instruction="Heighten cinematic pacing"
    )
    assert res["status"] == "REVIEW_PACKET_READY"
    assert "gemini_collaboration" in res
    assert "replit_staging" in res
    assert "measured_latency_ms" in res


def test_health_endpoint_is_explicit_about_runtime():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] in {"demo", "live"}
    assert isinstance(payload["providers"]["replit_environment"]["detected"], bool)
    assert "published" in payload["providers"]["replit_environment"]


def test_judge_ui_uses_truthful_snapshot_language():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    html = response.text
    assert "Save Review Snapshot" in html
    assert "Retrieving snapshot" in html
    assert "Review snapshot ID" in html
    assert "Active (3 Peers)" not in html
    assert "replit.app/stage/branch-01" not in html


def test_local_runtime_does_not_invent_public_url():
    status = replit_service.get_replit_status()
    if not status["is_replit_cloud"]:
        assert status["is_published_deployment"] is False
        assert status["public_url"] is None


def test_mode_badge_is_derived_from_backend_runtime_evidence():
    """The MODE badge must never be a static claim baked into the page."""
    html = TestClient(app).get("/").text
    badge = re.search(r'<span id="mode-badge"[^>]*>(.*?)</span>', html, re.S)
    assert badge is not None
    assert badge.group(1).strip() == "MODE: CHECKING RUNTIME"
    # It is populated from /api/v1/health.runtime_mode and the collaborate response.
    assert "'/api/v1/health'" in html
    assert "health.runtime_mode" in html
    assert "applyModeBadge(data.runtime_mode)" in html


def test_health_and_collaborate_report_the_same_runtime_mode():
    health_mode = TestClient(app).get("/api/v1/health").json()["runtime_mode"]
    collaborate = TestClient(app).post("/api/v1/forge/collaborate", json={}).json()
    assert collaborate["runtime_mode"] in {"demo", "live", "live_error"}
    # Without Gemini credentials the configured mode and the executed mode agree.
    if not settings.is_gemini_configured:
        assert health_mode == "demo"
        assert collaborate["runtime_mode"] == "demo"


def test_cors_is_not_credentialed_with_a_wildcard_origin():
    response = TestClient(app).get("/api/v1/health", headers={"Origin": "https://judge.example"})
    assert response.headers["access-control-allow-origin"] == "*"
    assert "access-control-allow-credentials" not in response.headers


def test_review_snapshots_are_bounded():
    saved = replit_service.review_snapshots
    replit_service.review_snapshots = type(saved)()
    try:
        cap = replit_service.MAX_REVIEW_SNAPSHOTS
        created = [
            replit_service.stage_scene_branch("room-bound", f"Scene {i}", "Script")["snapshot_id"]
            for i in range(cap + 5)
        ]
        assert len(replit_service.review_snapshots) == cap
        assert replit_service.get_review_snapshot(created[0]) is None
        assert replit_service.get_review_snapshot(created[-1]) is not None
        assert replit_service.get_replit_status()["review_snapshots_max"] == cap
    finally:
        replit_service.review_snapshots = saved


def test_repl_slug_is_not_fabricated_off_replit():
    status = replit_service.get_replit_status()
    if not status["is_replit_cloud"]:
        assert status["repl_slug"] == "local"


def test_vertex_default_location_supports_gemini_37():
    assert settings.GOOGLE_CLOUD_LOCATION == "global"


def test_gemini_runtime_mode_defaults_to_runtime_mode():
    from app.config import Settings
    s1 = Settings(RUNTIME_MODE="demo", GEMINI_RUNTIME_MODE="")
    assert s1.GEMINI_RUNTIME_MODE == "demo"
    s2 = Settings(RUNTIME_MODE="live", GEMINI_RUNTIME_MODE="")
    assert s2.GEMINI_RUNTIME_MODE == "live"
    s3 = Settings(RUNTIME_MODE="demo", GEMINI_RUNTIME_MODE="live")
    assert s3.RUNTIME_MODE == "demo"
    assert s3.GEMINI_RUNTIME_MODE == "live"


def test_replit_environment_evidence_is_independent_of_gemini_mode():
    from app.config import Settings
    # Changing runtime modes must never alter Replit environment detection
    s_demo = Settings(RUNTIME_MODE="demo", GEMINI_RUNTIME_MODE="demo")
    s_live = Settings(RUNTIME_MODE="live", GEMINI_RUNTIME_MODE="live")
    assert s_demo.is_replit_environment == s_live.is_replit_environment
    assert s_demo.replit_public_url == s_live.replit_public_url


def test_health_reports_gemini_and_replit_separately():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert "gemini_runtime_mode" in payload
    assert payload["gemini_runtime_mode"] in {"demo", "live"}
    # Verify google_gemini provider reports mode, configured, auth_type, auth_evidence, model
    gemini_info = payload["providers"]["google_gemini"]
    assert "mode" in gemini_info
    assert "configured" in gemini_info
    assert "auth_type" in gemini_info
    assert "auth_evidence" in gemini_info
    assert gemini_info["model"] == settings.GEMINI_MODEL
    assert gemini_info["auth_type"] in {"api_key", "vertex_ai", "none"}
    # Verify replit_environment provider is distinct and unaffected
    replit_info = payload["providers"]["replit_environment"]
    assert "detected" in replit_info
    assert "repl_slug" in replit_info
    assert "published" in replit_info


def test_gemini_auth_evidence_variants():
    from app.config import Settings
    unconfigured = Settings(GEMINI_API_KEY="", GOOGLE_CLOUD_PROJECT="")
    assert unconfigured.gemini_auth_type == "none"
    assert "No Gemini credentials" in unconfigured.gemini_auth_evidence

    api_key_auth = Settings(GEMINI_API_KEY="dummy-key-for-test", GOOGLE_CLOUD_PROJECT="")
    assert api_key_auth.gemini_auth_type == "api_key"
    assert "GEMINI_API_KEY environment variable present" in api_key_auth.gemini_auth_evidence
    # Crucial security check: the actual key must NEVER appear in auth_evidence
    assert "dummy-key-for-test" not in api_key_auth.gemini_auth_evidence

    vertex_auth = Settings(GEMINI_API_KEY="", GOOGLE_CLOUD_PROJECT="my-project", GOOGLE_CLOUD_LOCATION="global")
    assert vertex_auth.gemini_auth_type == "vertex_ai"
    assert "Vertex AI" in vertex_auth.gemini_auth_evidence


def test_live_gemini_fails_closed_without_client():
    orig_mode = gemini_service._runtime_mode
    orig_client = gemini_service.client
    try:
        gemini_service.runtime_mode = "live"
        gemini_service.client = None
        res = gemini_service.collaborate_on_scene(
            scene_title="Live Test Scene",
            working_script="INT. STUDIO - DAY",
            director_instruction="Test live fail closed"
        )
        assert res["success"] is False
        assert res["mode"] == "live_error"
        assert res["data"] is None
        assert "uninitialized" in res["error"].lower() or "not initialized" in res["error"].lower()
    finally:
        gemini_service._runtime_mode = orig_mode
        gemini_service.client = orig_client


@pytest.mark.asyncio
async def test_codirector_agent_fails_closed_on_live_error():
    orig_mode = gemini_service._runtime_mode
    orig_client = gemini_service.client
    try:
        gemini_service.runtime_mode = "live"
        gemini_service.client = None
        res = await codirector_agent.collaborate_and_stage(
            scene_title="Live Fail Scene",
            working_script="INT. STUDIO - DAY",
            director_instruction="Test agent live fail closed"
        )
        assert res["status"] == "LIVE_ERROR"
        assert res["runtime_mode"] == "live_error"
        assert "gemini_collaboration" not in res or res.get("gemini_collaboration") == {}
        assert "uninitialized" in res["error"].lower() or "not initialized" in res["error"].lower() or "failed" in res["error"].lower()
    finally:
        gemini_service._runtime_mode = orig_mode
        gemini_service.client = orig_client


def test_live_gemini_fails_closed_on_api_exception():
    from unittest.mock import MagicMock
    orig_mode = gemini_service._runtime_mode
    orig_client = gemini_service.client
    try:
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("429 Quota exceeded: Resource exhausted")
        gemini_service.runtime_mode = "live"
        gemini_service.client = mock_client

        res = gemini_service.collaborate_on_scene(
            scene_title="Live Quota Test Scene",
            working_script="INT. STUDIO - DAY",
            director_instruction="Test live exception fail closed"
        )
        assert res["success"] is False
        assert res["mode"] == "live_error"
        assert res["data"] is None
        assert "Quota exceeded" in res["error"]
    finally:
        gemini_service._runtime_mode = orig_mode
        gemini_service.client = orig_client


def test_live_gemini_success_with_mocked_client():
    import json
    from unittest.mock import MagicMock
    orig_mode = gemini_service._runtime_mode
    orig_client = gemini_service.client
    try:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_payload = {
            "enhanced_slugline": "EXT. CYBERPUNK ALLEY - NIGHT",
            "co_director_commentary": "Live execution mock test commentary.",
            "dialogue_refinements": [{"character": "Hero", "line": "Live test line.", "delivery_note": "Crisp"}],
            "camera_staging": {"shot_type": "Close Up", "lens_spec": "50mm", "lighting_setup": "Neon", "camera_movement": "Static"},
            "vfx_image_prompt": "Live test prompt",
            "sound_ambience": "Live drone"
        }
        mock_response.text = json.dumps(mock_payload)
        mock_client.models.generate_content.return_value = mock_response

        gemini_service.runtime_mode = "live"
        gemini_service.client = mock_client

        res = gemini_service.collaborate_on_scene(
            scene_title="Live Mock Test",
            working_script="INT. CYBERPUNK - NIGHT",
            director_instruction="Direct scene"
        )
        assert res["success"] is True
        assert res["mode"] == "live"
        assert "Google GenAI API" in res["evidence_source"]
        assert res["data"]["enhanced_slugline"] == "EXT. CYBERPUNK ALLEY - NIGHT"
    finally:
        gemini_service._runtime_mode = orig_mode
        gemini_service.client = orig_client

