from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from enum import Enum
import hashlib,json
class PolicyStatus(str,Enum):DRAFT="DRAFT"; APPROVED="APPROVED"; ACTIVE="ACTIVE"; RETIRED="RETIRED"
@dataclass
class PolicyVersion:
 policy_id:str; policy_version:int; created_at:str; effective_from:str|None; status:PolicyStatus; config_hash:str; config:dict
class PolicyStore:
 def __init__(self,audit=None):self.versions=[];self.audit=audit
 def create_draft(self,policy_id,config):
  version=1+max([p.policy_version for p in self.versions if p.policy_id==policy_id] or [0]);digest=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest();p=PolicyVersion(policy_id,version,datetime.now(timezone.utc).isoformat(),None,PolicyStatus.DRAFT,digest,dict(config));self.versions.append(p);return p
 def transition(self,policy_id,version,status,role):
  from .roles import Permission,authorize
  p=self.get(policy_id,version);target=PolicyStatus(status);allowed={PolicyStatus.DRAFT:{PolicyStatus.APPROVED},PolicyStatus.APPROVED:{PolicyStatus.ACTIVE},PolicyStatus.ACTIVE:{PolicyStatus.RETIRED}}
  authorize(role,Permission.POLICY_APPROVE if target in {PolicyStatus.APPROVED,PolicyStatus.ACTIVE} else Permission.POLICY_UPDATE)
  if target not in allowed.get(p.status,set()):raise ValueError("Invalid policy lifecycle transition.")
  if target==PolicyStatus.ACTIVE:
   for old in self.versions:
    if old.policy_id==policy_id and old.status==PolicyStatus.ACTIVE:old.status=PolicyStatus.RETIRED
   p.effective_from=datetime.now(timezone.utc).isoformat()
  p.status=target
  if self.audit and target in {PolicyStatus.ACTIVE,PolicyStatus.RETIRED}:self.audit.append("POLICY_ACTIVATED" if target==PolicyStatus.ACTIVE else "POLICY_RETIRED",actor_role=role,policy_id=policy_id,policy_version=version,config_hash=p.config_hash)
  return p
 def get(self,policy_id,version=None):
  matches=[p for p in self.versions if p.policy_id==policy_id and (version is None or p.policy_version==version)]
  if not matches:raise KeyError(policy_id)
  return matches[-1]
 def list(self):return [asdict(p) for p in self.versions]
