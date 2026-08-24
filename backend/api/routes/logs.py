"""
POST /ingest  — Accept log batches
GET  /logs    — Query stored log entries

Build target: Month 2.
"""

from fastapi import APIRouter

from backend.schemas.log_schema import IngestRequest, LogEntry

router = APIRouter(tags=["logs"])
_logs: list[LogEntry] = []


@router.post("/ingest", status_code=201)
def ingest(payload: IngestRequest) -> dict[str, int]:
    _logs.extend(payload.logs)
    return {"accepted": len(payload.logs), "total": len(_logs)}


@router.get("/logs", response_model=list[LogEntry])
def get_logs(limit: int = 100) -> list[LogEntry]:
    return _logs[-max(1, min(limit, 1000)) :]


def stored_logs() -> list[LogEntry]:
    return _logs
