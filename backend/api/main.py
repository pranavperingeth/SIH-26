import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import alerts, health, investigate, wallet

logger = logging.getLogger("chaintrace.api")
logging.basicConfig(level=logging.INFO)

# Create tables on startup. Phase 1 uses SQLite; this is fine for a
# hackathon build and keeps setup to a single command.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ChainTrace API",
    description="Real-time fraud-linked cryptocurrency exchange identification — Phase 1 backend foundation.",
    version="0.1.0",
)

# Phase 1: permissive local-development CORS. Tighten this in a later phase.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(health.router)
app.include_router(investigate.router)
app.include_router(wallet.router)
app.include_router(alerts.router)
