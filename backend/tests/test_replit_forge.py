import pytest
from fastapi.testclient import TestClient
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
