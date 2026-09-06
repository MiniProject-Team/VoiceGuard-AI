from dataclasses import dataclass,field,asdict
from datetime import datetime,timezone
from enum import Enum
from uuid import uuid4
class ReviewStatus(str,Enum):NOT_REQUIRED="NOT_REQUIRED"; PENDING_REVIEW="PENDING_REVIEW"; UNDER_REVIEW="UNDER_REVIEW"; RESOLVED="RESOLVED"; ESCALATED="ESCALATED"
class HumanAction(str,Enum):CONFIRM="CONFIRM"; OVERRIDE="OVERRIDE"; ESCALATE="ESCALATE"
class OverrideReason(str,Enum):KNOWN_FALSE_POSITIVE="KNOWN_FALSE_POSITIVE"; AUTHORIZED_EXCEPTION="AUTHORIZED_EXCEPTION"; VERIFIED_OUT_OF_BAND="VERIFIED_OUT_OF_BAND"; SYSTEM_ERROR="SYSTEM_ERROR"; OTHER="OTHER"
@dataclass
class DecisionRecord:
 session_id:str;ai_risk_score:float;ai_risk_level:str;ai_recommended_action:str;model_versions:dict;config_version:str
 decision_id:str=field(default_factory=lambda:f"DEC_{uuid4().hex.upper()}");human_review_status:ReviewStatus=ReviewStatus.PENDING_REVIEW;human_action:HumanAction|None=None;override_reason:OverrideReason|None=None;override_note:str|None=None;reviewed_by_role:str|None=None;timestamp:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
 def to_dict(self):return asdict(self)
 def review(self,action,role,reason=None,note=None,audit=None):
  from governance.roles import Permission,authorize
  action=HumanAction(action)
  if not role:raise PermissionError("Anonymous review is not allowed.")
  authorize(role,Permission.OVERRIDE_APPROVE if action==HumanAction.OVERRIDE else Permission.SESSION_REVIEW)
  if action==HumanAction.OVERRIDE:
   if not reason:raise ValueError("A controlled override reason is required.")
   reason=OverrideReason(reason)
   if reason==OverrideReason.OTHER and not note:raise ValueError("OTHER override reason requires a note.")
  self.human_action=action;self.override_reason=reason;self.override_note=note;self.reviewed_by_role=str(getattr(role,"value",role));self.human_review_status=ReviewStatus.ESCALATED if action==HumanAction.ESCALATE else ReviewStatus.RESOLVED
  if action==HumanAction.OVERRIDE and audit:audit.append("AI_DECISION_OVERRIDDEN",session_id=self.session_id,actor_role=role,decision_id=self.decision_id,original_risk_level=self.ai_risk_level,override_reason=reason.value)
  return self
