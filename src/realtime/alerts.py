"""Deduplicated local alert events and callback hooks; no external delivery."""
from __future__ import annotations
from datetime import datetime,timezone
from time import monotonic
from typing import Callable
LEVELS={"LOW":0,"MEDIUM":1,"HIGH":2,"CRITICAL":3}
class AlertManager:
    def __init__(self,enabled=True,cooldown_seconds=30.,minimum_level="HIGH",callback:Callable|None=None,clock=monotonic):self.enabled=enabled;self.cooldown=cooldown_seconds;self.minimum=minimum_level;self.callback=callback;self.clock=clock;self.last={}
    def consider(self,result:dict)->dict|None:
        level=result["risk_level"]
        if not self.enabled or LEVELS[level]<LEVELS[self.minimum]:return None
        key=(result["session_id"],level,result["decision"]);now=self.clock()
        if now-self.last.get(key,float("-inf"))<self.cooldown:return None
        self.last[key]=now;event={"event_type":"AlertTriggered","alert_type":"critical_voice_risk" if level=="CRITICAL" else "elevated_voice_risk","severity":level.lower(),"timestamp":datetime.now(timezone.utc).isoformat(),"session_id":result["session_id"],"segment_id":result["segment_id"],"message":"Potential AI voice impersonation or identity inconsistency detected.","recommended_action":result["recommended_action"]}
        if self.callback:self.callback(event)
        return event
