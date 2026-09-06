from dataclasses import dataclass,field,asdict
from datetime import datetime,timedelta,timezone
from enum import Enum
from uuid import uuid4
from .severity import Severity
class IncidentStatus(str,Enum):OPEN="OPEN"; TRIAGED="TRIAGED"; INVESTIGATING="INVESTIGATING"; CONTAINED="CONTAINED"; RESOLVED="RESOLVED"; CLOSED="CLOSED"
class IncidentCategory(str,Enum):SUSPECTED_VOICE_CLONE="SUSPECTED_VOICE_CLONE"; HUMAN_IMPOSTOR="HUMAN_IMPOSTOR"; REPLAY_SUSPECTED="REPLAY_SUSPECTED"; MODEL_FAILURE="MODEL_FAILURE"; DATA_PRIVACY_EVENT="DATA_PRIVACY_EVENT"; ENTERPRISE_INTEGRATION_FAILURE="ENTERPRISE_INTEGRATION_FAILURE"; UNKNOWN="UNKNOWN"
@dataclass
class Incident:
 session_id:str;severity:Severity;category:IncidentCategory;summary:str;risk_score:float;risk_level:str;assigned_to_role:str="SECURITY_OPERATOR";incident_id:str=field(default_factory=lambda:f"INC_{uuid4().hex.upper()}");created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat());status:IncidentStatus=IncidentStatus.OPEN;resolution:str|None=None;timeline:list=field(default_factory=list);recommended_actions:list=field(default_factory=list)
 def __post_init__(self):
  if not self.timeline:self.timeline.append({"at":self.created_at,"event":"INCIDENT_CREATED"})
 def to_dict(self):return asdict(self)
class IncidentStore:
 def __init__(self,deduplication_minutes=30):self.items={};self.window=timedelta(minutes=deduplication_minutes)
 def create(self,session_id,category,**kwargs):
  category=IncidentCategory(category);now=datetime.now(timezone.utc)
  for item in self.items.values():
   if item.session_id==session_id and item.category==category and item.status not in {IncidentStatus.RESOLVED,IncidentStatus.CLOSED} and now-datetime.fromisoformat(item.created_at)<=self.window:return item
  item=Incident(session_id=session_id,category=category,**kwargs);self.items[item.incident_id]=item;return item
 def get(self,incident_id):
  if incident_id not in self.items:raise KeyError(incident_id)
  return self.items[incident_id]
 def list(self):return [x.to_dict() for x in self.items.values()]
