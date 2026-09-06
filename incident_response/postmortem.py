from dataclasses import dataclass,asdict,field
from enum import Enum
class RootCause(str,Enum):MODEL_FALSE_NEGATIVE="MODEL_FALSE_NEGATIVE"; MODEL_FALSE_POSITIVE="MODEL_FALSE_POSITIVE"; UNKNOWN_GENERATOR="UNKNOWN_GENERATOR"; CHANNEL_DEGRADATION="CHANNEL_DEGRADATION"; SPEAKER_VERIFICATION_ERROR="SPEAKER_VERIFICATION_ERROR"; POLICY_ERROR="POLICY_ERROR"; SYSTEM_FAILURE="SYSTEM_FAILURE"; HUMAN_PROCESS_FAILURE="HUMAN_PROCESS_FAILURE"; UNKNOWN="UNKNOWN"
@dataclass
class Postmortem:
 incident_id:str;impact:str;detection:str;timeline:list;containment:str;root_cause:RootCause=RootCause.UNKNOWN;model_behavior:str="Not established";human_decisions:str="";what_worked:str="";what_failed:str="";corrective_actions:list=field(default_factory=list)
 def to_dict(self):return asdict(self)
def create_postmortem(incident,**fields):
 if incident.status.value not in {"RESOLVED","CLOSED"}:raise ValueError("Resolve incident before postmortem.")
 return Postmortem(incident_id=incident.incident_id,timeline=list(incident.timeline),**fields)
