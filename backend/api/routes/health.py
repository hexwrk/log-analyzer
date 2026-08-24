"""
GET /health — Liveness check, no auth required.
Returns model load status and DB connectivity.

Build target: Month 2.
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "database": "in-memory"}
