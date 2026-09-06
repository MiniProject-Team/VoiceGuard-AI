from dataclasses import dataclass
from datetime import datetime,timezone
from uuid import uuid4
@dataclass(frozen=True)
class PolicyException:
 exception_id:str;policy_id:str;reason:str;approved_by:str;expires_at:datetime;created_at:datetime
 def applies(self,now=None):return (now or datetime.now(timezone.utc))<self.expires_at
def create_exception(policy_id,reason,approved_by,expires_at,audit=None):
 if not reason or not approved_by:raise ValueError("Visible reason and approver are required.")
 if expires_at<=datetime.now(timezone.utc):raise ValueError("Exception must be time bounded in the future.")
 item=PolicyException(f"EXC_{uuid4().hex.upper()}",policy_id,reason,approved_by,expires_at,datetime.now(timezone.utc))
 if audit:audit.append("EXCEPTION_CREATED",actor_role=approved_by,exception_id=item.exception_id,policy_id=policy_id,expires_at=expires_at.isoformat())
 return item
