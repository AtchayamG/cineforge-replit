import os
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "CineForge Replit"
    TRACK: str = "Replit Partner Track"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Runtime Mode: 'live' or 'demo'
    RUNTIME_MODE: str = os.getenv("RUNTIME_MODE", "demo").lower()
    # Gemini Runtime Mode defaults to RUNTIME_MODE for backwards compatibility
    GEMINI_RUNTIME_MODE: str = os.getenv("GEMINI_RUNTIME_MODE", "").lower()
    
    # Google Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", 8004))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    CORS_ORIGINS: List[str] = ["*"]
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    ENABLE_MOCK_FALLBACK: bool = os.getenv("ENABLE_MOCK_FALLBACK", "false").lower() in ("true", "1", "yes")
    
    # Replit Environment Telemetry (Auto-detected in Replit Container)
    REPL_ID: str = os.getenv("REPL_ID", "")
    REPL_SLUG: str = os.getenv("REPL_SLUG", "")
    REPL_OWNER: str = os.getenv("REPL_OWNER", "")
    REPLIT_DEPLOYMENT_URL: str = os.getenv("REPLIT_DEPLOYMENT_URL", "")
    REPLIT_DOMAINS: str = os.getenv("REPLIT_DOMAINS", "")
    REPLIT_DEV_DOMAIN: str = os.getenv("REPLIT_DEV_DOMAIN", "")
    REPLIT_DEPLOYMENT: str = os.getenv("REPLIT_DEPLOYMENT", "")

    @model_validator(mode="after")
    def resolve_runtime_modes(self):
        self.RUNTIME_MODE = self.RUNTIME_MODE.lower() if self.RUNTIME_MODE else "demo"
        if not self.GEMINI_RUNTIME_MODE:
            self.GEMINI_RUNTIME_MODE = self.RUNTIME_MODE
        else:
            self.GEMINI_RUNTIME_MODE = self.GEMINI_RUNTIME_MODE.lower()
        return self

    @property
    def is_gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY or (self.GOOGLE_CLOUD_PROJECT and self.GOOGLE_CLOUD_LOCATION))

    @property
    def gemini_auth_type(self) -> str:
        if self.GEMINI_API_KEY:
            return "api_key"
        if self.GOOGLE_CLOUD_PROJECT and self.GOOGLE_CLOUD_LOCATION:
            return "vertex_ai"
        return "none"

    @property
    def gemini_auth_evidence(self) -> str:
        if self.GEMINI_API_KEY:
            return "GEMINI_API_KEY environment variable present"
        if self.GOOGLE_CLOUD_PROJECT and self.GOOGLE_CLOUD_LOCATION:
            return f"Vertex AI project ({self.GOOGLE_CLOUD_PROJECT}) and location ({self.GOOGLE_CLOUD_LOCATION})"
        return "No Gemini credentials configured"

    @property
    def is_replit_environment(self) -> bool:
        return bool(
            self.REPL_ID
            or self.REPLIT_DOMAINS
            or self.REPLIT_DEV_DOMAIN
            or self.REPLIT_DEPLOYMENT
            or os.getenv("REPLIT_ENVIRONMENT")
        )

    @property
    def replit_public_url(self) -> str:
        if self.REPLIT_DEPLOYMENT_URL:
            return self.REPLIT_DEPLOYMENT_URL.rstrip("/")
        domain = next((item.strip() for item in self.REPLIT_DOMAINS.split(",") if item.strip()), "")
        if not domain:
            return ""
        return domain.rstrip("/") if domain.startswith("http") else f"https://{domain.rstrip('/')}"

settings = Settings()
