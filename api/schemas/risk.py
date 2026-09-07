from typing import Literal
from pydantic import Field
from .common import StrictModel

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]

class RiskResult(StrictModel):
    score: float = Field(ge=0, le=100)
    level: RiskLevel
    decision: str
    recommended_action: str | None = None
    reasons: list[str] = Field(default_factory=list)

class AlertResponse(StrictModel):
    severity: str
    alert_type: str
    message: str
    recommended_action: str

class SegmentResult(StrictModel):
    segment_id: int
    synthetic_probability: float | None = Field(default=None, ge=0, le=1)
    speaker_similarity: float | None = Field(default=None, ge=-1, le=1)
    risk_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel
    decision: str
    recommended_action: str | None = None
    speaker_verification_status: str = "unavailable"
    speaker_verified: bool | None = None
    synthetic_detection_status: str = "unavailable"
    reasons: list[str] = Field(default_factory=list)
