from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
ALLOWED={"confirmed_genuine","confirmed_impersonation","unknown","TRUE_POSITIVE","FALSE_POSITIVE","TRUE_NEGATIVE","FALSE_NEGATIVE","UNCERTAIN"}
def record_feedback(path,event_id,label,scores,context,authorized=False):
 if not authorized:raise PermissionError("Feedback requires an authorized operator.")
 if label not in ALLOWED:raise ValueError("Invalid feedback label.")
 record={"event_id":event_id,"label":label,"model_scores":scores,"context_metadata":context,"timestamp":datetime.now(timezone.utc).isoformat()};target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
 with target.open("a",encoding="utf-8") as stream:stream.write(json.dumps(record)+"\n")
 return record
