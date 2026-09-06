from __future__ import annotations
from collections import Counter,deque
from statistics import mean
import numpy as np
class MetricsCollector:
 def __init__(self,max_samples=10000):self.active_sessions=0;self.sessions_completed=0;self.segments_processed=0;self.alerts_triggered=0;self.system_errors=Counter();self.degraded_events=0;self.latencies=deque(maxlen=max_samples);self.rtf=deque(maxlen=max_samples);self.synthetic=deque(maxlen=max_samples);self.speaker=deque(maxlen=max_samples);self.risks=deque(maxlen=max_samples);self.risk_levels=Counter()
 def session_started(self):self.active_sessions+=1
 def session_completed(self):self.active_sessions=max(0,self.active_sessions-1);self.sessions_completed+=1
 def record(self,*,latency,rtf=None,synthetic=None,speaker=None,risk=None,level="UNKNOWN",alert=False,degraded=False):
  self.segments_processed+=1;self.latencies.append(float(latency));self.risk_levels[level]+=1;self.alerts_triggered+=int(alert);self.degraded_events+=int(degraded)
  for target,value in ((self.rtf,rtf),(self.synthetic,synthetic),(self.speaker,speaker),(self.risks,risk)):
   if value is not None:target.append(float(value))
 def error(self,kind):self.system_errors[kind]+=1
 def summary(self):
  lat=list(self.latencies);total=self.segments_processed
  def stats(values):return {"count":len(values),"mean":mean(values) if values else None,"min":min(values) if values else None,"max":max(values) if values else None}
  return {"active_sessions":self.active_sessions,"sessions_completed":self.sessions_completed,"segments_processed":total,"latency":{"average_ms":mean(lat)*1000 if lat else None,"p95_ms":float(np.percentile(lat,95)*1000) if lat else None},"average_rtf":mean(self.rtf) if self.rtf else None,"score_distributions":{"synthetic":stats(self.synthetic),"speaker":stats(self.speaker),"risk":stats(self.risks)},"risk_distribution":dict(self.risk_levels),"alerts_triggered":self.alerts_triggered,"errors":dict(self.system_errors),"error_rate":sum(self.system_errors.values())/total if total else 0,"degraded_mode_events":self.degraded_events}
