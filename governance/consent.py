from dataclasses import dataclass
from datetime import datetime,timezone
from enum import Enum

class ConsentStatus(str,Enum):
 NOT_REQUIRED="NOT_REQUIRED"; NOT_REQUESTED="NOT_REQUESTED"; REQUESTED="REQUESTED"; GRANTED="GRANTED"; DENIED="DENIED"; WITHDRAWN="WITHDRAWN"
@dataclass(frozen=True)
class ConsentRecord:
 speaker_id:str; status:ConsentStatus; purpose:str; consent_timestamp:str|None=None
 def __post_init__(self):
  if self.status==ConsentStatus.GRANTED and not self.consent_timestamp:object.__setattr__(self,"consent_timestamp",datetime.now(timezone.utc).isoformat())
 def permits(self,purpose:str)->bool:return self.status in {ConsentStatus.GRANTED,ConsentStatus.NOT_REQUIRED} and self.purpose==purpose
def enrollment_consent(speaker_id,status,purpose="voice verification for protected organizational workflows",timestamp=None):
 return ConsentRecord(speaker_id,ConsentStatus(status),purpose,timestamp)
