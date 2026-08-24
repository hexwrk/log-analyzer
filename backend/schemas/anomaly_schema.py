"""
Pydantic validation schema.
Build target: Month 2.
"""
from datetime import datetime

from pydantic import BaseModel


class AnomalyResponse(BaseModel):
	id: int
	timestamp: datetime
	src_ip: str
	score: float
	threat_type: str = "UNKNOWN"
	reason: str = ""
