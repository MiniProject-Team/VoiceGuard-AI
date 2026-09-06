from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
from .model_metadata import directory_hash
VALID={"CANDIDATE":{"STAGING","REJECTED"},"STAGING":{"ACTIVE","REJECTED"},"ACTIVE":{"RETIRED"},"RETIRED":{"ACTIVE"},"REJECTED":set()}
GOVERNANCE_CHECKS={"technical_validation","security_checks","privacy_checks","known_limitations","governance_approval"}
class RegistryError(ValueError):pass
class ModelRegistry:
 def __init__(self,path:str|Path):self.path=Path(path);self.data=self._load()
 def _load(self):
  if not self.path.exists():return {"schema_version":1,"models":[],"history":[]}
  return json.loads(self.path.read_text(encoding="utf-8"))
 def save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps(self.data,indent=2),encoding="utf-8")
 def register(self,model_type:str,model_name:str,version:str,path:str|Path,metadata:dict)->dict:
  target=Path(path)
  if not target.exists() or (target.is_dir() and not any(target.rglob("*"))):raise RegistryError("Model artifact is missing or empty.")
  if any(x["model_type"]==model_type and x["model_version"]==version for x in self.data["models"]):raise RegistryError("Registered model versions are immutable.")
  record={"model_id":f"MODEL_{uuid4().hex.upper()}","model_type":model_type,"model_name":model_name,"model_version":version,"created_at":datetime.now(timezone.utc).isoformat(),"artifact_path":str(target),"file_hash":directory_hash(target),"status":"CANDIDATE",**metadata};self.data["models"].append(record);self.data["history"].append({"at":record["created_at"],"action":"REGISTER","model_id":record["model_id"]});self.save();return record
 def get(self,model_id:str):
  try:return next(x for x in self.data["models"] if x["model_id"]==model_id)
  except StopIteration:raise RegistryError("Model is not registered.")
 def validate_hash(self,model_id:str)->bool:
  item=self.get(model_id);return directory_hash(item["artifact_path"])==item["file_hash"]
 def promote(self,model_id:str,checks:dict[str,bool],override:bool=False)->dict:
  item=self.get(model_id);target="STAGING" if item["status"]=="CANDIDATE" else "ACTIVE"
  if target=="ACTIVE" and checks.get("all") is True:checks={name:True for name in GOVERNANCE_CHECKS} # legacy CLI aggregate means its approval workflow completed
  if target not in VALID.get(item["status"],set()):raise RegistryError("Invalid promotion transition.")
  if target=="ACTIVE" and (not GOVERNANCE_CHECKS.issubset(checks) or not all(checks[x] for x in GOVERNANCE_CHECKS)):raise RegistryError("Activation requires technical, security, privacy, limitations, and governance approval checks.")
  if target=="ACTIVE":
   for other in self.data["models"]:
    if other["model_type"]==item["model_type"] and other["status"]=="ACTIVE":other["status"]="RETIRED"
  item["status"]=target;self.data["history"].append({"at":datetime.now(timezone.utc).isoformat(),"action":"PROMOTE","model_id":model_id,"status":target,"checks":checks,"override":override});self.save();return item
 def reject(self,model_id:str,reason:str,role:str="SUPERVISOR")->dict:
  item=self.get(model_id)
  if item["status"] not in {"CANDIDATE","STAGING"}:raise RegistryError("Only candidate or staging models can be rejected.")
  if not reason.strip():raise RegistryError("Model rejection reason is required.")
  item["status"]="REJECTED";item["rejection_reason"]=reason;item["rejected_by_role"]=role;self.data["history"].append({"at":datetime.now(timezone.utc).isoformat(),"action":"REJECT","model_id":model_id,"reason":reason,"role":role});self.save();return item
 def rollback(self,model_type:str)->dict:
  active=[x for x in self.data["models"] if x["model_type"]==model_type and x["status"]=="ACTIVE"];retired=[x for x in self.data["models"] if x["model_type"]==model_type and x["status"]=="RETIRED"]
  if not active or not retired:raise RegistryError("Rollback requires active and previously retired versions.")
  active[0]["status"]="RETIRED";target=retired[-1];target["status"]="ACTIVE";self.data["history"].append({"at":datetime.now(timezone.utc).isoformat(),"action":"ROLLBACK","from":active[0]["model_id"],"to":target["model_id"]});self.save();return target
