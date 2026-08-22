from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.agents.codirector_agent import codirector_agent
from app.services.replit_environment_service import replit_service

router = APIRouter(prefix="/forge", tags=["CineForge Replit Studio"])

class CollaborationRequest(BaseModel):
    scene_title: str = Field(default="Scene 1: Sector 9 Atmospheric Breach")
    working_script: str = Field(default="EXT. NEO-TOKYO RUNWAY - NIGHT")
    director_instruction: str = Field(default="Heighten tension and add 35mm anamorphic camera cues.")

class StagingRequest(BaseModel):
    room_id: str = Field(default="room-alpha-sector9")
    scene_title: str = Field(default="Scene 1: Sector 9 Atmospheric Breach")
    script_content: str = Field(default="EXT. NEO-TOKYO RUNWAY - NIGHT")

@router.post("/collaborate")
async def collaborate_scene(request: CollaborationRequest):
    """
    Produces a Gemini co-direction packet and an in-session review snapshot.
    """
    return await codirector_agent.collaborate_and_stage(
        scene_title=request.scene_title,
        working_script=request.working_script,
        director_instruction=request.director_instruction
    )

@router.get("/replit/environment")
async def get_replit_env():
    """
    Returns evidence derived from Replit's predefined runtime variables.
    """
    return replit_service.get_replit_status()

@router.post("/stage")
async def stage_preview(request: StagingRequest):
    """
    Creates an in-memory review snapshot; it does not create a Replit branch.
    """
    return replit_service.stage_scene_branch(
        room_id=request.room_id,
        scene_title=request.scene_title,
        script_content=request.script_content
    )

@router.get("/snapshots/{snapshot_id}")
async def get_review_snapshot(snapshot_id: str):
    """
    Retrieves an existing in-session review snapshot by ID.

    Snapshots are intentionally process-local and disappear when the app restarts.
    """
    snapshot = replit_service.get_review_snapshot(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Review snapshot not found in the current app session.")
    return snapshot
