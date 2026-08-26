import asyncio
import logging
import time
from typing import Dict, Any
from app.config import settings
from app.services.gemini_service import gemini_service
from app.services.replit_environment_service import replit_service

logger = logging.getLogger("cineforge.codirector")

class CoDirectorAgent:
    """
    Replit-hosted Co-Director Agent powered by Gemini 3.7 Flash.
    Engages in real-time script refinement, camera lens suggestions,
    VFX prompt generation, and instant 1-click preview staging.
    """
    def __init__(self):
        self.name = "CoDirectorAgent"
        self.role = "Replit Collaborative AI Co-Director"

    @property
    def gemini_runtime_mode(self) -> str:
        return settings.GEMINI_RUNTIME_MODE

    @property
    def runtime_mode(self) -> str:
        return settings.GEMINI_RUNTIME_MODE

    async def collaborate_and_stage(self, scene_title: str, working_script: str, director_instruction: str) -> Dict[str, Any]:
        start = time.time()
        
        # Step 1: Gemini collaborative co-direction
        gemini_res = await asyncio.to_thread(
            gemini_service.collaborate_on_scene,
            scene_title,
            working_script,
            director_instruction,
        )
        if not gemini_res.get("success"):
            return {
                "agent": self.name,
                "scene_title": scene_title,
                "status": "LIVE_ERROR",
                "runtime_mode": gemini_res.get("mode", "live_error"),
                "gemini_runtime_mode": self.gemini_runtime_mode,
                "gemini_evidence_source": gemini_res.get("evidence_source"),
                "error": gemini_res.get("error", "Gemini collaboration failed."),
                "measured_latency_ms": round((time.time() - start) * 1000, 2)
            }
        scene_data = gemini_res.get("data", {})

        # Step 2: Create a truthful, in-session review snapshot.
        stage_res = replit_service.stage_scene_branch(
            room_id="room-alpha-sector9",
            scene_title=scene_title,
            script_content=working_script
        )

        return {
            "agent": self.name,
            "scene_title": scene_title,
            "status": "REVIEW_PACKET_READY",
            # The mode that actually executed
            "runtime_mode": gemini_res.get("mode"),
            "gemini_runtime_mode": self.gemini_runtime_mode,
            "gemini_collaboration": scene_data,
            "gemini_evidence_source": gemini_res.get("evidence_source"),
            "replit_staging": stage_res,
            "replit_environment": replit_service.get_replit_status(),
            "measured_latency_ms": round((time.time() - start) * 1000, 2)
        }

codirector_agent = CoDirectorAgent()
