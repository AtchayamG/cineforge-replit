import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.routes.forge_routes import router as forge_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")
logger = logging.getLogger("cineforge.main")

app = FastAPI(
    title="CineForge Replit Studio API",
    version="1.0.0",
    description="Cloud cinema review sandbox powered by Replit and Google Gemini 3.7 Flash."
)

# Public read-only demo: no cookies or Authorization headers are used, so the
# wildcard origin is kept without credentialed CORS (which browsers reject anyway).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(forge_router, prefix=settings.API_PREFIX)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
@app.get("/ui")
async def serve_ui():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "service": settings.PROJECT_NAME,
        "track": settings.TRACK,
        "mode": settings.RUNTIME_MODE,
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "track": settings.TRACK,
        "runtime_mode": settings.RUNTIME_MODE,
        "providers": {
            "google_gemini": {
                "configured": settings.is_gemini_configured,
                "model": settings.GEMINI_MODEL
            },
            "replit_environment": {
                "detected": settings.is_replit_environment,
                "repl_slug": settings.REPL_SLUG,
                "published": settings.REPLIT_DEPLOYMENT == "1" or bool(settings.REPLIT_DOMAINS),
                "public_url": settings.replit_public_url or None
            }
        }
    }
