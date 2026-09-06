"""Safe human-readable explanation formatting."""
from __future__ import annotations
def format_assessment(result: dict) -> str:
    reasons="\n".join(f"- {reason}" for reason in result["reasons"]) or "- No elevated-risk rule was triggered."
    return f"VOICEGUARD RISK ASSESSMENT\n==========================\n\nRisk Score: {result['risk_score']:.2f}/100\nRisk Level: {result['risk_level']}\n\nDecision:\n{result['decision']}\n\nRecommended Action:\n{result['recommended_action']}\n\nReasons:\n{reasons}"
