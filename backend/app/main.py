from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, health, incidents, meta, queue
from app.config import settings

app = FastAPI(title="Luma Málaga API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(incidents.router, prefix=settings.api_prefix)
app.include_router(queue.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(meta.router, prefix=settings.api_prefix)