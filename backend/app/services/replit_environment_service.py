import os
import time
import hashlib
import logging
from collections import OrderedDict
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("cineforge.replit_env")

class ReplitEnvironmentService:
    """
    Replit Cloud Runtime & Container Telemetry Service for CineForge.
    Inspects host Replit runtime parameters and creates review snapshots inside
    the running app. It does not claim to create Replit branches or deployments.
    """
    # Snapshots are public, unauthenticated, and process-local, so the store is a
    # bounded FIFO: the oldest entry is evicted once the cap is reached.
    MAX_REVIEW_SNAPSHOTS = 50

    def __init__(self):
        self.repl_id = settings.REPL_ID
        self.repl_slug = settings.REPL_SLUG
        self.repl_owner = settings.REPL_OWNER
        self.deployment_url = settings.replit_public_url
        self.review_snapshots: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()

    def get_replit_status(self) -> Dict[str, Any]:
        """
        Returns environment metadata for the host Replit container or local sandbox.
        """
        is_cloud = settings.is_replit_environment
        is_published = settings.REPLIT_DEPLOYMENT == "1" or bool(settings.REPLIT_DOMAINS)
        return {
            "is_replit_cloud": is_cloud,
            "is_published_deployment": is_published,
            "repl_slug": self.repl_slug or "local",
            "repl_id": self.repl_id or None,
            "repl_owner": self.repl_owner or None,
            "deployment_target": "Replit published app" if is_published else "Local or Replit development runtime",
            "one_click_run_status": "RUNNING_ON_REPLIT" if is_cloud else "CONFIG_PRESENT_NOT_CLOUD_VERIFIED",
            "public_url": self.deployment_url or None,
            "review_snapshots_active": len(self.review_snapshots),
            "review_snapshots_max": self.MAX_REVIEW_SNAPSHOTS,
            "runtime_evidence": "Replit predefined environment variables" if is_cloud else "Local runtime inspection"
        }

    def stage_scene_branch(self, room_id: str, scene_title: str, script_content: str) -> Dict[str, Any]:
        """
        Creates an in-memory review snapshot. Replit Publishing remains the
        mechanism that produces the public deployment URL.
        """
        digest = hashlib.sha256(f"{room_id}\n{scene_title}\n{script_content}".encode("utf-8")).hexdigest()[:10]
        snapshot_id = f"review-{int(time.time())}-{digest}"
        review_url = f"{self.deployment_url}/?snapshot={snapshot_id}" if self.deployment_url else None
        snapshot = {
            "status": "REVIEW_SNAPSHOT_CREATED",
            "snapshot_id": snapshot_id,
            "scene_title": scene_title,
            "review_url": review_url,
            "created_at": time.time(),
            "environment": "Replit runtime" if settings.is_replit_environment else "Local verification runtime",
            "persistence": "in_memory_until_restart",
            "message": "Review snapshot created in the current app session.",
            "retention": f"most recent {self.MAX_REVIEW_SNAPSHOTS} snapshots in this process"
        }
        self.review_snapshots[snapshot_id] = snapshot
        while len(self.review_snapshots) > self.MAX_REVIEW_SNAPSHOTS:
            evicted, _ = self.review_snapshots.popitem(last=False)
            logger.info("Evicted oldest review snapshot %s (cap %s).", evicted, self.MAX_REVIEW_SNAPSHOTS)
        return snapshot

    def get_review_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a snapshot only while it remains in this process's session."""
        return self.review_snapshots.get(snapshot_id)

replit_service = ReplitEnvironmentService()
