"""Chapter Agent — API application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, compliance, controls, evidence, scorer, scorecard, solutions, traces


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Chapter Agent Platform",
        description="AI governance platform — guardrails, evaluation, compliance gates",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(solutions.router, prefix="/api")
    app.include_router(compliance.router, prefix="/api")
    app.include_router(controls.router, prefix="/api")
    app.include_router(evidence.router, prefix="/api")
    app.include_router(traces.router, prefix="/api")
    app.include_router(scorecard.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(scorer.router, prefix="/api")

    return app


app = create_app()
