from typing import Literal
from pydantic import Field
from .common import StrictModel

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"]

class RiskResult(StrictModel):
    score: float = Field(ge=0, le=100)
    level: RiskLevel
    decision: str
    recommended_action: str | None = None

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
