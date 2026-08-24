"""
Pydantic validation schema.
Build target: Month 2.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
	timestamp: datetime
	src_ip: str
	dst_ip: str | None = None
	src_port: int | None = Field(default=None, ge=0, le=65535)
	dst_port: int | None = Field(default=None, ge=0, le=65535)
	protocol: str | None = None
	bytes_sent: int = Field(default=0, ge=0)
	bytes_recv: int = Field(default=0, ge=0)
	duration_ms: float = Field(default=0, ge=0)
	action: str | None = None
	raw: str | None = None


class IngestRequest(BaseModel):
	logs: list[LogEntry] = Field(min_length=1, max_length=10_000)
