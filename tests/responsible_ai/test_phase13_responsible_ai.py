import pytest
from responsible_ai.decision_record import DecisionRecord
from responsible_ai.review_queue import ReviewQueue
from responsible_ai.human_oversight import can_proceed
from governance.governance_log import GovernanceLog
def record():return DecisionRecord("s",.98,"CRITICAL","BLOCK_OR_ESCALATE",{"detector":"v1"},"cfg-v1")
def test_override_authorization_reason_and_preservation():
 item=record();audit=GovernanceLog()
 with pytest.raises(PermissionError):item.review("OVERRIDE","VIEWER","SYSTEM_ERROR",audit=audit)
 with pytest.raises(ValueError):item.review("OVERRIDE","SUPERVISOR")
 item.review("OVERRIDE","SUPERVISOR","VERIFIED_OUT_OF_BAND",audit=audit);assert item.ai_risk_level=="CRITICAL" and audit.records[-1]["event"]=="AI_DECISION_OVERRIDDEN"
def test_queue_and_critical_guard():
 q=ReviewQueue();item=record();q.add(item);q.claim(item.decision_id);q.decide(item.decision_id,"ESCALATE","ANALYST");assert item.human_review_status.value=="ESCALATED"
 assert not can_proceed("CRITICAL",True) and not can_proceed("CRITICAL",True,True,False) and can_proceed("CRITICAL",True,True,True)
