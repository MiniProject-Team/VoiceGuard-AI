from datetime import datetime,timezone
from threading import Lock
from .decision_record import ReviewStatus
class ReviewQueue:
 def __init__(self):self._items={};self._lock=Lock()
 def should_queue(self,risk_level,high_value=False,detector_disagreement=False,high_uncertainty=False,degraded=False):return str(risk_level).upper()=="CRITICAL" or (str(risk_level).upper()=="HIGH" and high_value) or detector_disagreement or high_uncertainty or degraded
 def add(self,record,**signals):
  if not self.should_queue(record.ai_risk_level,**signals):return None
  with self._lock:record.human_review_status=ReviewStatus.PENDING_REVIEW;self._items[record.decision_id]=record
  return record
 def claim(self,decision_id):
  item=self.get(decision_id)
  if item.human_review_status!=ReviewStatus.PENDING_REVIEW:raise ValueError("Review is not pending.")
  item.human_review_status=ReviewStatus.UNDER_REVIEW;return item
 def decide(self,decision_id,*args,**kwargs):return self.get(decision_id).review(*args,**kwargs)
 def get(self,decision_id):
  if decision_id not in self._items:raise KeyError(decision_id)
  return self._items[decision_id]
 def list(self,status=None):return [x.to_dict() for x in self._items.values() if status is None or x.human_review_status==ReviewStatus(status)]
