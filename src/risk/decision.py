"""Configuration-driven score levels and security actions."""
from __future__ import annotations
from typing import Any
def risk_level(score: float, thresholds: dict[str,Any]) -> str:
    if score<=float(thresholds["low_max"]):return "LOW"
    if score<=float(thresholds["medium_max"]):return "MEDIUM"
    if score<=float(thresholds["high_max"]):return "HIGH"
    return "CRITICAL"
def decision_for(level: str, decisions: dict[str,Any]) -> tuple[str,str]:
    policy=decisions[level.lower()];return policy["decision"],policy["recommended_action"]
