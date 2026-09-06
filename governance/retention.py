from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from enum import Enum
from typing import Callable
class HoldState(str,Enum):NORMAL="NORMAL"; SECURITY_HOLD="SECURITY_HOLD"; LEGAL_HOLD="LEGAL_HOLD"
@dataclass
class RetentionRecord:
 record_id:str; category:str; created_at:datetime; hold:HoldState=HoldState.NORMAL; sensitive_data:object=None
class RetentionPolicy:
 def __init__(self,periods=None):self.periods=periods or {"temporary_audio":timedelta(minutes=0),"session_metadata":timedelta(days=30),"security_events":timedelta(days=180),"incident_records":timedelta(days=180),"speaker_enrollment":timedelta(days=365),"audit_logs":timedelta(days=365)}
 def expires_at(self,record):return record.created_at+self.periods[record.category]
 def expired(self,record,now=None):return record.hold==HoldState.NORMAL and (now or datetime.now(timezone.utc))>=self.expires_at(record)
 def cleanup(self,records,delete:Callable|None=None,now=None,audit=None):
  removed=[];kept=[]
  for record in records:
   if self.expired(record,now):
    if delete:delete(record)
    removed.append(record.record_id)
    if audit:audit.append("RETENTION_DELETION",record_id=record.record_id,category=record.category)
   else:kept.append(record)
  return {"deleted":removed,"retained":kept}
def authorized_delete(record_id,category,role,delete,audit):
 from .roles import Permission,authorize
 authorize(role,Permission.ENROLLMENT_DELETE if category=="speaker_enrollment" else Permission.SESSION_DELETE)
 delete(record_id);return audit.append("SPEAKER_DELETED" if category=="speaker_enrollment" else "RETENTION_DELETION",actor_role=role,record_id=record_id,category=category)
