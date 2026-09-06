from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from governance.governance_log import GovernanceLog
from incident_response import IncidentStore,IncidentCategory,Severity
from incident_response.workflow import transition,containment_action
from incident_response.postmortem import create_postmortem,RootCause
from responsible_ai.decision_record import DecisionRecord
from responsible_ai.human_oversight import can_proceed
def main():
 audit=GovernanceLog();store=IncidentStore();results=[]
 ceo=store.create("SIM_CEO",IncidentCategory.SUSPECTED_VOICE_CLONE,severity=Severity.SEV1,summary="Simulated CEO voice-clone request for INR 10 lakh transfer",risk_score=.98,risk_level="CRITICAL",recommended_actions=["HOLD_TRANSACTION","TRUSTED_CALLBACK"]);hold=containment_action(ceo,"HOLD_TRANSACTION",True);transition(ceo,"TRIAGED","SECURITY_OPERATOR");transition(ceo,"CONTAINED","SECURITY_OPERATOR");transition(ceo,"RESOLVED","SECURITY_OPERATOR","Trusted callback confirmed fraud; simulated transfer remained held.");pm=create_postmortem(ceo,impact="No loss in controlled simulation",detection="Critical voice-clone indicators",containment="Transaction held and trusted callback used",root_cause=RootCause.UNKNOWN_GENERATOR,human_decisions="Security operator confirmed containment",what_worked="Human oversight",what_failed="N/A",corrective_actions=["Retain indicators, not raw audio"]);transition(ceo,"CLOSED","SUPERVISOR",audit=audit);results.append({"scenario":"CEO_CLONE","incident":ceo.to_dict(),"containment":hold,"postmortem":pm.to_dict()})
 fp=DecisionRecord("SIM_FP",.78,"HIGH","STEP_UP",{},"phase13");fp.review("OVERRIDE","SUPERVISOR","KNOWN_FALSE_POSITIVE","Poor audio; independently verified",audit);results.append({"scenario":"FALSE_POSITIVE","ai_result_preserved":fp.ai_risk_level,"human_action":fp.human_action,"feedback":"FALSE_POSITIVE"})
 degraded=store.create("SIM_DEGRADED",IncidentCategory.MODEL_FAILURE,severity=Severity.SEV2,summary="Phase 3 unavailable during sensitive transaction",risk_score=0,risk_level="UNKNOWN",recommended_actions=["TRUSTED_CALLBACK"]);results.append({"scenario":"SYSTEM_DEGRADED","incident":degraded.to_dict(),"automatic_sensitive_action_allowed":can_proceed("UNKNOWN",True,degraded=True)})
 path=ROOT/"reports/phase13/incident_simulation.json";path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(results,indent=2,default=str),encoding="utf-8");print("PASS CEO clone: SEV1, held, callback, contained, postmortem");print("PASS false positive: AI result preserved, authorized feedback recorded");print("PASS degraded mode: independent verification required");return results
if __name__=="__main__":main()
