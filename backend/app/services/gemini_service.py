import os
import json
import logging
import time
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("cineforge.gemini")

class GeminiService:
    """
    Google GenAI SDK & Gemini 3.7 Flash integration service for CineForge.
    Provides real-time co-direction, collaborative screenplay enhancement, camera direction,
    and instantaneous visual staging prompt compilation.
    """
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self._runtime_mode: Optional[str] = None
        self.client = None
        self._init_client()

    @property
    def runtime_mode(self) -> str:
        if self._runtime_mode is not None:
            return self._runtime_mode
        return settings.GEMINI_RUNTIME_MODE

    @runtime_mode.setter
    def runtime_mode(self, value: Optional[str]):
        self._runtime_mode = value.lower() if value else None

    @property
    def api_key(self) -> str:
        return settings.GEMINI_API_KEY

    @property
    def project(self) -> str:
        return settings.GOOGLE_CLOUD_PROJECT

    @property
    def location(self) -> str:
        return settings.GOOGLE_CLOUD_LOCATION

    def _init_client(self):
        if self.api_key or (self.project and self.location):
            try:
                from google import genai
                if self.api_key:
                    self.client = genai.Client(api_key=self.api_key)
                else:
                    self.client = genai.Client(vertexai=True, project=self.project, location=self.location)
                logger.info(f"Initialized Google GenAI Client with model: {self.model_name} (Mode: LIVE)")
            except Exception as e:
                self.client = None
                logger.warning(f"Could not initialize google-genai client ({e}).")
        else:
            self.client = None
            logger.info("No Gemini credentials found. Running in deterministic DEMO fixture mode.")

    def collaborate_on_scene(self, scene_title: str, working_script: str, director_instruction: str) -> Dict[str, Any]:
        """
        Executes Gemini-powered scene co-direction and visual staging.
        """
        start_time = time.time()
        prompt = f"""
        You are an elite Hollywood Co-Director and Visual Script Architect collaborating in real-time on Replit.
        Scene Title: {scene_title}
        Working Script Draft:
        {working_script}

        Director Instruction:
        {director_instruction}

        Output JSON strictly matching this schema:
        {{
            "enhanced_slugline": "string",
            "co_director_commentary": "string",
            "dialogue_refinements": [
                {{"character": "string", "line": "string", "delivery_note": "string"}}
            ],
            "camera_staging": {{
                "shot_type": "string",
                "lens_spec": "string",
                "lighting_setup": "string",
                "camera_movement": "string"
            }},
            "vfx_image_prompt": "string",
            "sound_ambience": "string"
        }}
        """

        if self.runtime_mode == "live":
            # Attempt lazy init if credentials were provided after startup
            if self.client is None and settings.is_gemini_configured:
                self._init_client()

            if not self.client:
                logger.error("Live Gemini requested, but Gemini client is uninitialized.")
                return {
                    "success": False,
                    "mode": "live_error",
                    "evidence_source": f"Google GenAI API ({self.model_name} live - unconfigured)",
                    "error": "Live Gemini mode requested but Gemini client is uninitialized (missing API key or Vertex credentials).",
                    "data": None
                }

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config={
                        "system_instruction": "You are a real-time collaborative film co-director assisting in an interactive studio session.",
                        "response_mime_type": "application/json"
                    }
                )
                result = json.loads(response.text.strip())
                latency_ms = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "mode": "live",
                    "evidence_source": f"Google GenAI API ({self.model_name} live)",
                    "data": result,
                    "latency_ms": latency_ms
                }
            except Exception as e:
                logger.error(f"Gemini live scene collaboration failed: {e}")
                # Fail closed: never silently fall back to fixtures in live mode!
                return {
                    "success": False,
                    "mode": "live_error",
                    "evidence_source": f"Google GenAI API ({self.model_name} live)",
                    "error": str(e),
                    "data": None
                }

        # Deterministic Demo Mode (Local Fixture)
        latency_ms = max(int((time.time() - start_time) * 1000), 24)
        demo_data = {
            "enhanced_slugline": "EXT. NEO-TOKYO RUNWAY - SECTOR 9 - NIGHT (RAIN)",
            "co_director_commentary": "Heightened cinematic stakes by introducing subtle telemetry arcing and contrasting Maya's calm investigative posture with the worsening atmospheric storm.",
            "dialogue_refinements": [
                {
                    "character": "Maya Vance",
                    "line": "Echo, pull the sector telemetry immediately. The core containment grid shouldn't be purging until dawn.",
                    "delivery_note": "Stern, low vocal cadence with rising tension"
                },
                {
                    "character": "Echo (AI Voice)",
                    "line": "Containment integrity has dropped to 38%. Something inside the core memory banks is rejecting our override.",
                    "delivery_note": "Calm, digitized synthetic alert with subtle frequency flutter"
                }
            ],
            "camera_staging": {
                "shot_type": "Low Angle Tracking Medium Shot",
                "lens_spec": "35mm Panavision Anamorphic, f/2.0",
                "lighting_setup": "Dual-tone: Cyan key light from rain reflections, pulsing crimson rim from server exhaust",
                "camera_movement": "Slow continuous dolly-in tracking Maya's boots through water puddles"
            },
            "vfx_image_prompt": "Cinematic 35mm film still, female detective Maya Vance in dark charcoal coat on rain-slicked runway, glowing holographic telemetry in hand, Panavision anamorphic lens flares, cyan and crimson neon lighting, photorealistic, 8k resolution",
            "sound_ambience": "Heavy tropical downpour, sub-bass 60Hz ambient synth drone, digitized glitch warning pulses"
        }

        return {
            "success": True,
            "mode": "demo",
            "evidence_source": "Deterministic Collaborative Scene Fixture (demo mode)",
            "data": demo_data,
            "latency_ms": latency_ms
        }

gemini_service = GeminiService()
