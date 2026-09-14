from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""

    configure_logging()

    yield


app = FastAPI(
    title="Async Fetcher",
    description=("Production-oriented asynchronous URL fetcher built with FastAPI."),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(
    router,
    prefix="/api/v1",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Return application health status."""

    return {
        "status": "ok",
    }
