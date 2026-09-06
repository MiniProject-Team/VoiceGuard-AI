from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class EnterpriseAction:
    mode:str;status:str;required_controls:list[str];source_decision:str
def simulate_enterprise_action(decision:str)->EnterpriseAction:
    """Local fallback only; does not contact or control a bank system."""
    if decision in {"BLOCK_OR_ESCALATE","BLOCK","ESCALATE"}:return EnterpriseAction("SIMULATION MODE","HOLD FOR REVIEW",["MFA","Trusted callback","Supervisor approval"],decision)
    if decision=="STEP_UP_VERIFICATION":return EnterpriseAction("SIMULATION MODE","PENDING VERIFICATION",["MFA","Trusted callback"],decision)
    if decision=="MONITOR":return EnterpriseAction("SIMULATION MODE","MONITOR",["Enhanced monitoring"],decision)
    return EnterpriseAction("SIMULATION MODE","NO HOLD REQUESTED",["Normal application controls"],decision)
