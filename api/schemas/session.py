from datetime import datetime
from typing import Literal
from pydantic import Field
from .common import StrictModel
from .risk import RiskLevel, SegmentResult

SessionStatus = Literal["created", "active", "stopping", "completed", "failed"]

class SessionContext(StrictModel):
    call_origin: str | None = Field(default=None, max_length=100)
    contact_match: bool | None = None
    transaction_amount: float | None = Field(default=None, ge=0)
    transaction_type: str | None = Field(default=None, max_length=100)
    privileged_action: bool | None = None
    historical_fraud_indicator: bool | None = None
    new_device: bool | None = None
    unusual_time: bool | None = None
    location_anomaly: bool | None = None

class CreateSessionRequest(StrictModel):
    speaker_id: str | None = Field(default=None, min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_.-]+$")
    context: SessionContext = Field(default_factory=SessionContext)

class CreateSessionResponse(StrictModel):
    session_id: str
    status: SessionStatus
    created_at: datetime

class SessionResponse(StrictModel):
    session_id: str
    status: SessionStatus
    speaker_id: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    segments_processed: int
    current_risk_score: float
    current_risk_level: RiskLevel

class StopSessionResponse(StrictModel):
    session_id: str
    status: SessionStatus
    segments_processed: int
    highest_risk_score: float
    final_risk_level: RiskLevel

class SessionResultsResponse(StrictModel):
    session_id: str
    results: list[SegmentResult]
    limit: int
    offset: int
    total: int
