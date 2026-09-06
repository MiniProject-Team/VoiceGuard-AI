from __future__ import annotations
import hashlib,json,threading
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
from .integrity import canonical_json
from .redaction import redact

GENESIS="0"*64
class AuditLog:
    def __init__(self,path:str|Path,config_hash:str):self.path=Path(path);self.config_hash=config_hash;self._lock=threading.Lock();self._previous=self._read_last_hash()
    def _read_last_hash(self):
        if not self.path.exists():return GENESIS
        lines=[line for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return json.loads(lines[-1])["record_hash"] if lines else GENESIS
    def append(self,event_type:str,session_id:str|None=None,**fields:Any)->dict[str,Any]:
        with self._lock:
            record={"event_id":f"EVENT_{uuid4().hex.upper()}","session_id":session_id,"timestamp":datetime.now(timezone.utc).isoformat(),"event_type":event_type,"risk_score":fields.get("risk_score"),"risk_level":fields.get("risk_level"),"decision":fields.get("decision"),"engine_version":fields.get("engine_version"),"config_version":fields.get("config_version"),"config_hash":self.config_hash,"model_versions":fields.get("model_versions",{}),"previous_hash":self._previous}
            record=redact(record);record["record_hash"]=hashlib.sha256(canonical_json(record)).hexdigest();self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open("a",encoding="utf-8") as stream:stream.write(json.dumps(record,sort_keys=True)+"\n")
            self._previous=record["record_hash"];return record

def verify_audit_chain(path:str|Path)->dict[str,Any]:
    target=Path(path);previous=GENESIS;count=0;errors=[]
    if not target.exists():return {"valid":True,"records":0,"errors":[],"status":"NOT TESTED - no audit records"}
    for number,line in enumerate(target.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():continue
        try:record=json.loads(line);stored=record.pop("record_hash");expected=hashlib.sha256(canonical_json(record)).hexdigest()
        except Exception:errors.append({"line":number,"error":"malformed_record"});continue
        if record.get("previous_hash")!=previous:errors.append({"line":number,"error":"broken_previous_hash"})
        if stored!=expected:errors.append({"line":number,"error":"record_hash_mismatch"})
        previous=stored;count+=1
    return {"valid":not errors,"records":count,"errors":errors,"status":"PASS" if not errors else "FAIL"}
