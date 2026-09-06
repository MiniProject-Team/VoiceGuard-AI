"""Bounded recent-result statistics independent of Phase 5 smoothing."""
from __future__ import annotations
from collections import deque
import numpy as np
class ResultAggregator:
    def __init__(self,max_segments=20):self.results=deque(maxlen=max_segments);self.maximum_risk=0.;self.consecutive_high=0
    def add(self,result:dict)->dict:
        self.results.append(result);score=float(result["risk_score"]);self.maximum_risk=max(self.maximum_risk,score)
        self.consecutive_high=self.consecutive_high+1 if result["risk_level"] in {"HIGH","CRITICAL"} else 0
        return {"current_risk":score,"maximum_risk":self.maximum_risk,"average_recent_risk":float(np.mean([x["risk_score"] for x in self.results])),"consecutive_high_count":self.consecutive_high}
