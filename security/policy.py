from __future__ import annotations
DEGRADED_RECOMMENDATION="Required security components are unavailable. Require independent verification before authorizing sensitive action."
def enforce_fail_safe(result:dict)->dict:
    missing=result.get("errors",[]) or []
    if missing:
        result={**result,"status":"SYSTEM_DEGRADED","decision":"STEP_UP_VERIFICATION","recommended_action":DEGRADED_RECOMMENDATION}
        if result.get("risk_level")=="LOW":result["risk_level"]="UNKNOWN"
    return result
def validate_explanation(result:dict)->bool:return result.get("risk_level") not in {"HIGH","CRITICAL"} or bool(result.get("reasons"))
def policy_consistent(level:str,decision:str)->bool:
    allowed={"LOW":{"ALLOW"},"MEDIUM":{"MONITOR"},"HIGH":{"STEP_UP_VERIFICATION"},"CRITICAL":{"BLOCK_OR_ESCALATE","ESCALATE","BLOCK"},"UNKNOWN":{"STEP_UP_VERIFICATION","NO_ANALYSIS"}}
    return decision in allowed.get(level,set())
