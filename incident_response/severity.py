from enum import IntEnum
class Severity(IntEnum):SEV1=1;SEV2=2;SEV3=3;SEV4=4
def assess_severity(risk_score=0,risk_level="LOW",financial_impact=0,privileged_action=False,confirmed_loss=False,system_compromise=False,high_value_threshold=1_000_000,weights=None):
 weights=weights or {"high_value_transaction":2,"privileged_action":2,"confirmed_loss":3,"system_compromise":3}
 points=0
 if str(risk_level).upper()=="CRITICAL" or risk_score>=.9:points+=2
 elif str(risk_level).upper()=="HIGH" or risk_score>=.7:points+=1
 if financial_impact>=high_value_threshold:points+=weights["high_value_transaction"]
 if privileged_action:points+=weights["privileged_action"]
 if confirmed_loss:points+=weights["confirmed_loss"]
 if system_compromise:points+=weights["system_compromise"]
 return Severity.SEV1 if points>=4 else Severity.SEV2 if points>=2 else Severity.SEV3 if points>=1 else Severity.SEV4
