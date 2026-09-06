from dataclasses import asdict, dataclass
from enum import Enum

class AttackFamily(str, Enum):
    TEXT_TO_SPEECH="TEXT_TO_SPEECH"; VOICE_CONVERSION="VOICE_CONVERSION"; VOICE_CLONING="VOICE_CLONING"
    REPLAY="REPLAY"; RE_RECORDED_SYNTHETIC="RE_RECORDED_SYNTHETIC"; CODEC_DEGRADED_SYNTHETIC="CODEC_DEGRADED_SYNTHETIC"
    UNKNOWN_SYNTHETIC="UNKNOWN_SYNTHETIC"; HUMAN_IMPOSTOR="HUMAN_IMPOSTOR"; UNKNOWN="UNKNOWN"

def attack_family(value: object) -> AttackFamily:
    try: return AttackFamily(str(value).upper())
    except (ValueError, TypeError): return AttackFamily.UNKNOWN

@dataclass(frozen=True)
class AttackMetadata:
    attack_family: str="UNKNOWN"; generator_family: str="UNKNOWN"; channel_type: str="UNKNOWN"; replay_status: str="UNKNOWN"
    language: str="UNKNOWN"; codec: str="UNKNOWN"; noise_condition: str="UNKNOWN"; source_dataset: str="UNKNOWN"
    @classmethod
    def from_mapping(cls, data: dict | None):
        data=data or {}; allowed=cls.__dataclass_fields__; clean={k:(str(data.get(k)) if data.get(k) not in (None,"") else "UNKNOWN") for k in allowed};clean["attack_family"]=attack_family(clean["attack_family"]).value;return cls(**clean)
    def to_dict(self): return asdict(self)
