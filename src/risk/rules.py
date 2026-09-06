"""Explainable combination rules for security-important interactions."""
from __future__ import annotations
from typing import Any
from .schema import RiskInput

def apply_rules(value: RiskInput, normalized_synthetic: float | None, normalized_similarity: float | None,
                config: dict[str, Any]) -> tuple[dict[str,float],list[str]]:
    contributions={"clone_attack_bonus":0.,"speaker_mismatch_bonus":0.};reasons=[]
    if normalized_synthetic is not None and normalized_similarity is not None and normalized_synthetic>=float(config["synthetic_high_threshold"]) and normalized_similarity>=float(config["clone_similarity_threshold"]):
        contributions["clone_attack_bonus"]=float(config["clone_attack_bonus"]);reasons.append("Voice closely matches the enrolled speaker but contains strong synthetic-speech indicators.")
    if value.speaker_verified is False and value.claimed_identity is not False:
        contributions["speaker_mismatch_bonus"]=float(config["speaker_mismatch_bonus"]);reasons.append("Incoming voice does not sufficiently match the enrolled speaker.")
    return contributions,reasons
