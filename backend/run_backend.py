import uvicorn
import os
import sys

# Ensure backend directory is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings

if __name__ == "__main__":
    print(f"==================================================")
    print(f"🎬 Starting {settings.PROJECT_NAME} ({settings.TRACK})")
    print(f"⚡ Mode: {settings.RUNTIME_MODE.upper()}")
    print(f"🌐 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📖 Swagger Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"==================================================")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=False)
