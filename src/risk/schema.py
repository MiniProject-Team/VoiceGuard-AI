"""Serializable, optional-field risk input schema."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class RiskInput:
    synthetic_probability: float | None = None
    speaker_similarity: float | None = None
    speaker_mismatch_probability: float | None = None
    speaker_verified: bool | None = None
    speaker_verification_status: str | None = None
    claimed_identity: bool | None = None
    call_origin: str | None = None
    contact_match: bool | None = None
    known_contact: bool | None = None
    transaction_amount: float | None = None
    transaction_type: str | None = None
    privileged_action: bool | None = None
    historical_fraud_indicator: bool | None = None
    new_device: bool | None = None
    unusual_time: bool | None = None
    location_anomaly: bool | None = None
    session_id: str | None = None
    threat_intelligence_risk: float | None = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)
    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "RiskInput":
        allowed = cls.__dataclass_fields__.keys(); unknown = set(values) - set(allowed)
        if unknown: raise ValueError(f"Unknown risk input fields: {sorted(unknown)}")
        return cls(**values)
