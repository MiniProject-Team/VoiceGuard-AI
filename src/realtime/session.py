"""Privacy-preserving in-memory call state."""
from __future__ import annotations
from dataclasses import dataclass,field
from datetime import datetime,timezone
from typing import Any
from .aggregator import ResultAggregator
@dataclass
class CallSession:
    session_id:str;speaker_id:str|None=None;context:dict[str,Any]=field(default_factory=dict);max_history_segments:int=20;start_time:datetime=field(default_factory=lambda:datetime.now(timezone.utc));segment_count:int=0;current_risk:float=0.;highest_risk:float=0.;decision:str="ALLOW";critical_alerts:int=0
    def __post_init__(self):self.aggregator=ResultAggregator(self.max_history_segments)
    def record(self,result:dict)->dict:
        self.segment_count+=1;state=self.aggregator.add(result);self.current_risk=state["current_risk"];self.highest_risk=state["maximum_risk"];self.decision=result["decision"];return state
    def summary(self,duration_seconds:float)->dict:
        final=self.aggregator.results[-1] if self.aggregator.results else {}
        return {"session_id":self.session_id,"duration_seconds":duration_seconds,"segments_processed":self.segment_count,"highest_risk_score":self.highest_risk,"final_risk_level":final.get("risk_level","UNKNOWN"),"critical_alerts":self.critical_alerts,"decision":self.decision,"recommended_action":final.get("recommended_action","No voiced segments were processed.")}
