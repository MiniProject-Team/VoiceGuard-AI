import pytest
from incident_response import *
from incident_response.triage import triage
from incident_response.workflow import transition
from incident_response.postmortem import create_postmortem
from governance.governance_log import GovernanceLog
def test_severity_and_deduplication_postmortem():
 assert assess_severity(.98,"CRITICAL",1_000_000)==Severity.SEV1
 store=IncidentStore();args=dict(severity=Severity.SEV1,summary="risk interaction",risk_score=.98,risk_level="CRITICAL");one=store.create("s",IncidentCategory.SUSPECTED_VOICE_CLONE,**args);assert store.create("s",IncidentCategory.SUSPECTED_VOICE_CLONE,**args) is one
 triage(one,"SECURITY_OPERATOR",financial_impact=1_000_000);transition(one,"CONTAINED","SECURITY_OPERATOR");transition(one,"RESOLVED","SECURITY_OPERATOR","contained");assert create_postmortem(one,impact="none",detection="AI plus context",containment="held").root_cause.value=="UNKNOWN"
def test_auditor_cannot_modify_incident():
 item=Incident("s",Severity.SEV3,IncidentCategory.UNKNOWN,"x",.2,"LOW")
 with pytest.raises(PermissionError):triage(item,"AUDITOR")
