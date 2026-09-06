from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import uuid4
from .roles import Permission,authorize
@dataclass(frozen=True)
class RiskAcceptance:
 risk_id:str;description:str;severity:str;accepted_by_role:str;expiration:datetime;mitigation:str;created_at:str
 def active(self,now=None):return (now or datetime.now(timezone.utc))<self.expiration
def accept_risk(description,severity,accepted_by_role,expiration,mitigation,audit=None):
 authorize(accepted_by_role,Permission.POLICY_APPROVE)
 if severity.upper()=="CRITICAL" and not mitigation:raise ValueError("Critical residual risk requires mitigation.")
 if expiration<=datetime.now(timezone.utc):raise ValueError("Risk acceptance must expire in the future.")
 item=RiskAcceptance(f"RISK_{uuid4().hex.upper()}",description,severity.upper(),str(getattr(accepted_by_role,"value",accepted_by_role)),expiration,mitigation,datetime.now(timezone.utc).isoformat())
 if audit:audit.append("RISK_ACCEPTED",actor_role=accepted_by_role,risk_id=item.risk_id,severity=item.severity,expiration=expiration.isoformat())
 return item
