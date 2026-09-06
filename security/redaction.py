from __future__ import annotations
import re
from pathlib import Path
from typing import Any

SENSITIVE_KEYS = {"authorization","access_token","token","api_key","secret","webhook_secret","speaker_embedding","embedding","raw_audio","audio_path","file_path"}
EMAIL = re.compile(r"(?<![\w.])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<!\w)(?:\+91[\s-]?)?[6-9]\d{9}(?!\w)")

def redact_text(value: str) -> str:
    value = EMAIL.sub("[REDACTED_EMAIL]", value); return PHONE.sub("[REDACTED_PHONE]", value)

def redact(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in SENSITIVE_KEYS: return "[REDACTED]"
    if isinstance(value, dict): return {k:redact(v,k) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [redact(item) for item in value]
    if isinstance(value, Path): return "[REDACTED_PATH]"
    return redact_text(value) if isinstance(value,str) else value
