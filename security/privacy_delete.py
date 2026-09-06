from __future__ import annotations
from pathlib import Path
from .input_validation import validate_speaker_id
def delete_enrolled_speaker(speaker_id:str,embedding_dir:str|Path)->list[str]:
    safe=validate_speaker_id(speaker_id);root=Path(embedding_dir).resolve();removed=[]
    for suffix in (".npy",".json"):
        target=(root/f"{safe}{suffix}").resolve()
        if target.parent!=root:raise ValueError("Unsafe enrollment path.")
        if target.exists():target.unlink();removed.append(target.name)
    cache=root/"cache"
    # Shared extraction caches cannot be reliably attributed without an ownership index; never delete unrelated cache entries.
    return removed
