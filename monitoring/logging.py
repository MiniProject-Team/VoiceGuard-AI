from __future__ import annotations
import json,logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from security.redaction import redact
class JsonFormatter(logging.Formatter):
 def format(self,record):return json.dumps(redact({"level":record.levelname,"logger":record.name,"message":record.getMessage()}),default=str)
def configure_rotating_json(path,level="INFO",max_size_mb=20,backups=5):
 target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);handler=RotatingFileHandler(target,maxBytes=int(max_size_mb*1024*1024),backupCount=backups,encoding="utf-8");handler.setFormatter(JsonFormatter());logger=logging.getLogger("voiceguard");logger.setLevel(level);logger.addHandler(handler);return logger
