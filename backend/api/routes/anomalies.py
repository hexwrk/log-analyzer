"""
GET /anomalies       — Paginated anomaly list
GET /anomalies/{id}  — Single anomaly detail with feature breakdown

Build target: Month 2.
"""
from fastapi import APIRouter, HTTPException

from backend.api.routes.logs import stored_logs
from backend.schemas.anomaly_schema import AnomalyResponse

router = APIRouter(tags=["anomalies"])


@router.get("/anomalies", response_model=list[AnomalyResponse])
def get_anomalies(limit: int = 100) -> list[AnomalyResponse]:
	results = []
	for index, entry in enumerate(stored_logs(), start=1):
		if entry.action and entry.action.upper() in {"BLOCK", "DENY", "FAIL"}:
			results.append(
				AnomalyResponse(
					id=index,
					timestamp=entry.timestamp,
					src_ip=entry.src_ip,
					score=1.0,
					threat_type="SUSPICIOUS_ACTION",
					reason=f"Action was {entry.action.upper()}",
				)
			)
	return results[-max(1, min(limit, 1000)) :]


@router.get("/anomalies/{anomaly_id}", response_model=AnomalyResponse)
def get_anomaly(anomaly_id: int) -> AnomalyResponse:
	anomaly = next(
		(item for item in get_anomalies(1000) if item.id == anomaly_id),
		None,
	)
	if anomaly is None:
		raise HTTPException(status_code=404, detail="Anomaly not found")
	return anomaly
