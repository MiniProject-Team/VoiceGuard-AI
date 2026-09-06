"""Optional contextual modifiers with explicit unknown handling."""
from __future__ import annotations
from typing import Any
from .schema import RiskInput

def evaluate_context(value: RiskInput, config: dict[str, Any]) -> tuple[float, list[str], list[str]]:
    modifiers=config["modifiers"];score=0.;reasons=[];missing=[]
    def add(condition: bool, key: str, reason: str):
        nonlocal score
        if condition: score += float(modifiers.get(key,0));reasons.append(reason)
    if value.transaction_amount is None: missing.append("transaction_amount")
    else:add(value.transaction_amount>=float(config["transaction"]["high_value_threshold"]),"high_value_transaction","High-value transaction requested during voice interaction.")
    for field,key,reason in (("privileged_action","privileged_action","Privileged or sensitive action requested."),("historical_fraud_indicator","historical_fraud_indicator","Historical fraud indicators are associated with this interaction."),("unusual_time","unusual_time","Interaction occurred at an unusual time."),("new_device","new_device","Interaction originated from a new device."),("location_anomaly","location_anomaly","Location anomaly was reported.")):
        current=getattr(value,field)
        if current is None:missing.append(field)
        else:add(current,key,reason)
    if value.contact_match is None:missing.append("contact_match")
    else:add(not value.contact_match,"contact_mismatch","Contact information does not match the expected contact.")
    if value.call_origin is None:missing.append("call_origin")
    elif value.call_origin=="unknown":add(True,"unknown_caller","Caller origin is unknown.")
    elif value.call_origin=="suspicious":add(True,"suspicious_caller","Caller origin is marked suspicious.")
    elif value.call_origin!="known":raise ValueError("call_origin must be known, unknown, suspicious, or null")
    return score,reasons,missing
