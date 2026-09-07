from typing import Literal
from pydantic import Field
from .common import StrictModel
from .risk import AlertResponse, RiskResult

class AnalysisSignals(StrictModel):
    synthetic_probability: float | None = Field(default=None, ge=0, le=1)
    speaker_similarity: float | None = Field(default=None, ge=-1, le=1)
    synthetic_detection_status: str = "unavailable"
    speaker_verification_status: str = "unavailable"
    speaker_verified: bool | None = None

class AnalysisResponse(StrictModel):
    session_id: str
    segment_id: int
    status: Literal["completed"]
    analysis: AnalysisSignals
    risk: RiskResult
    alert: AlertResponse | None = None
