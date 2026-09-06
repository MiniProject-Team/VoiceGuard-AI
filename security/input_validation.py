from __future__ import annotations
import re
from pathlib import Path,PurePath
SPEAKER_ID=re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
def validate_speaker_id(value:str)->str:
    if not SPEAKER_ID.fullmatch(value) or value in {".",".."}:raise ValueError("Invalid speaker identifier.")
    return value
def safe_filename(value:str)->str:
    name=PurePath(value.replace("\\","/")).name
    if name!=value or name in {"",".",".."}:raise ValueError("Unsafe filename.")
    return name
def validate_upload_header(data:bytes,extension:str)->None:
    extension=extension.lower().lstrip(".")
    valid=(extension=="wav" and len(data)>=12 and data[:4] in {b"RIFF",b"RF64"} and data[8:12]==b"WAVE") or (extension=="flac" and data.startswith(b"fLaC"))
    if not valid:raise ValueError("Audio content does not match its declared format.")
