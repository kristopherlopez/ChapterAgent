"""Chapter Agent — API application."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env from project root
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from src.api.routes import catalog, chat, compliance, controls, evaluate, evidence, onboard, scorer, solutions, traces


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Chapter Agent Platform",
        description="AI governance platform — guardrails, evaluation, compliance gates",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_origin_regex=r"http://localhost:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(catalog.router, prefix="/api")
    app.include_router(solutions.router, prefix="/api")
    app.include_router(compliance.router, prefix="/api")
    app.include_router(controls.router, prefix="/api")
    app.include_router(evidence.router, prefix="/api")
    app.include_router(traces.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(scorer.router, prefix="/api")
    app.include_router(evaluate.router, prefix="/api")
    app.include_router(onboard.router, prefix="/api")

    return app


app = create_app()
