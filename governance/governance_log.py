from __future__ import annotations
import hashlib,json,threading
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4

ALLOWED_EVENTS={"POLICY_ACTIVATED","POLICY_RETIRED","AI_DECISION_OVERRIDDEN","RETENTION_CHANGED","RETENTION_DELETION","INCIDENT_CLOSED","MODEL_ACCEPTED","MODEL_REJECTED","SPEAKER_DELETED","EXCEPTION_CREATED","RISK_ACCEPTED"}
class GovernanceLog:
 def __init__(self,path=None):self.path=Path(path) if path else None;self.records=[];self._lock=threading.Lock();self._previous="0"*64
 def append(self,event_type,session_id=None,actor_role=None,**details):
  event_type=str(event_type).upper()
  if event_type not in ALLOWED_EVENTS:raise ValueError("Unsupported governance event type.")
  safe={k:v for k,v in details.items() if k not in {"raw_audio","speaker_embedding","secret_token","personal_identifier"}}
  record={"event_id":f"GOV_{uuid4().hex.upper()}","event":event_type,"session_id":session_id,"actor_role":getattr(actor_role,"value",actor_role),"timestamp":datetime.now(timezone.utc).isoformat(),"details":safe,"previous_hash":self._previous}
  record["record_hash"]=hashlib.sha256(json.dumps(record,sort_keys=True,default=str).encode()).hexdigest()
  with self._lock:
   self.records.append(record);self._previous=record["record_hash"]
   if self.path:self.path.parent.mkdir(parents=True,exist_ok=True);self.path.open("a",encoding="utf-8").write(json.dumps(record,default=str)+"\n")
  return record
