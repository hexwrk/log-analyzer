"""
SecureFlow — FastAPI application entry point.
Build target: Month 2 (API layer).
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.api.routes.health import router as health_router
from backend.api.routes.anomalies import router as anomalies_router
from backend.api.routes.logs import router as logs_router

app = FastAPI(title="SecureFlow API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(logs_router)
app.include_router(anomalies_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
