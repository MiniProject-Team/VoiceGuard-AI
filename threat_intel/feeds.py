from abc import ABC, abstractmethod
from pathlib import Path
import json, yaml

class ThreatFeed(ABC):
    @abstractmethod
    def get_indicators(self) -> list[str]: ...

class LocalThreatFeed(ThreatFeed):
    def __init__(self,path): self.path=Path(path)
    def get_indicators(self):
        data=json.loads(self.path.read_text(encoding="utf-8")) if self.path.suffix.lower()==".json" else yaml.safe_load(self.path.read_text(encoding="utf-8"))
        values=data.get("known_attack_patterns",[]) if isinstance(data,dict) else []
        return [str(x) for x in values if isinstance(x,str)]
