from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import hashlib
@dataclass(frozen=True)
class EvidenceReference:
 session_id:str;artifact_type:str;sha256:str;timestamp:str;reference:str;raw_audio_included:bool=False
def evidence_reference(session_id,artifact_type,artifact,reference,allow_raw_audio=False):
 if artifact_type.lower()=="raw_audio" and not allow_raw_audio:raise PermissionError("Raw audio evidence requires explicit retention authorization.")
 data=artifact if isinstance(artifact,bytes) else str(artifact).encode();return EvidenceReference(session_id,artifact_type,hashlib.sha256(data).hexdigest(),datetime.now(timezone.utc).isoformat(),reference,artifact_type.lower()=="raw_audio")
