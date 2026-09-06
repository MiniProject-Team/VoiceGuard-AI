from datetime import datetime,timedelta,timezone
import pytest
from governance.roles import *
from governance.consent import *
from governance.governance_log import GovernanceLog
from governance.policy import PolicyStore
from governance.retention import *
from governance.exceptions import create_exception
from governance.risk_acceptance import accept_risk
def test_roles_and_security_boundaries():
 assert has_permission(Role.ANALYST,SESSION_REVIEW) and not has_permission(Role.VIEWER,OVERRIDE_APPROVE)
 assert not has_permission(Role.ANALYST,POLICY_UPDATE) and not has_permission(Role.AUDITOR,INCIDENT_CLOSE)
 assert not has_permission(Role.VIEWER,ENROLLMENT_DELETE)
def test_consent_purpose():
 c=enrollment_consent("pseudonymous-speaker",ConsentStatus.GRANTED,"speaker verification");assert c.permits("speaker verification") and not c.permits("marketing")
def test_retention_hold_and_audit():
 old=datetime.now(timezone.utc)-timedelta(days=40);normal=RetentionRecord("s1","session_metadata",old);held=RetentionRecord("s2","session_metadata",old,HoldState.LEGAL_HOLD);audit=GovernanceLog();r=RetentionPolicy().cleanup([normal,held],audit=audit);assert r["deleted"]==["s1"] and r["retained"]==[held] and audit.records[0]["event"]=="RETENTION_DELETION"
def test_policy_versioning_lifecycle():
 audit=GovernanceLog();s=PolicyStore(audit);one=s.create_draft("step-up",{"threshold":.8});two=s.create_draft("step-up",{"threshold":.9});assert (one.policy_version,two.policy_version)==(1,2);s.transition("step-up",2,"APPROVED",Role.SUPERVISOR);s.transition("step-up",2,"ACTIVE",Role.SUPERVISOR);assert audit.records[-1]["event"]=="POLICY_ACTIVATED"
 with pytest.raises(PermissionError):s.transition("step-up",1,"APPROVED",Role.ANALYST)
def test_exception_and_risk_expiry():
 future=datetime.now(timezone.utc)+timedelta(hours=1);e=create_exception("p","maintenance","SUPERVISOR",future);assert e.applies();assert accept_risk("calibration","HIGH",Role.SUPERVISOR,future,"step-up verification").active()
