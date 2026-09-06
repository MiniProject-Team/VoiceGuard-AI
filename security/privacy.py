from __future__ import annotations
import hashlib, hmac, os
from pathlib import Path
from typing import Any
import yaml

def load_privacy_config(path: str|Path="configs/privacy.yaml") -> dict[str,Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def pseudonymize(identifier: str, prefix: str="SUBJECT", key: bytes|None=None) -> str:
    key_material=key or os.environ.get("VOICEGUARD_PSEUDONYM_KEY","voiceguard-demo-nonproduction").encode(); digest=hmac.new(key_material,identifier.encode(),hashlib.sha256).hexdigest()[:16].upper(); return f"{prefix}_{digest}"

def retained_assessment(record: dict[str,Any]) -> dict[str,Any]:
    allowed={"session_id","segment_id","timestamp","synthetic_probability","speaker_similarity","risk_score","risk_level","decision","alert_event","engine_version","config_version","config_hash","model_versions"}; return {key:value for key,value in record.items() if key in allowed}

def assert_privacy_defaults(config: dict[str,Any]) -> None:
    if config["audio"]["retain_raw_audio"]: raise ValueError("Raw audio retention must be disabled in hardened mode.")
