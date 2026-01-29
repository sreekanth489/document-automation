from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers import upload, automation
from app.config import get_settings
from app.services.extractors import check_provider_availability


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Document Automation API",
        description="Extract data from passport and G-28 forms, then auto-fill web forms",
        version="1.0.0"
    )

    # CORS middleware for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create directories
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.screenshot_dir).mkdir(parents=True, exist_ok=True)

    # Mount static files for screenshots
    app.mount(
        "/screenshots",
        StaticFiles(directory=settings.screenshot_dir),
        name="screenshots"
    )

    # Include routers
    app.include_router(upload.router)
    app.include_router(automation.router)

    @app.get("/")
    async def root():
        return {
            "message": "Document Automation API",
            "docs": "/docs",
            "endpoints": {
                "upload": "POST /api/upload",
                "extract": "GET /api/extract/{session_id}",
                "fill_form": "POST /api/fill-form",
                "screenshot": "GET /api/screenshot/{filename}"
            }
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/api/provider-status")
    async def provider_status():
        """Check the status of the configured extraction provider."""
        settings = get_settings()
        status = await check_provider_availability()
        return {
            "configured_provider": settings.extraction_provider.value,
            "available": status["available"],
            "message": status["message"],
            "config": {
                "ollama_base_url": settings.ollama_base_url,
                "ollama_text_model": settings.ollama_text_model,
                "ollama_vision_model": settings.ollama_vision_model,
                "ocr_engine": settings.ocr_engine,
            }
        }

    return app


app = create_app()
