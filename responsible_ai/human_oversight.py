from dataclasses import dataclass
from enum import Enum
class OversightAction(str,Enum):AUTOMATED_NORMAL="AUTOMATED_NORMAL"; MONITOR="MONITOR"; INDEPENDENT_VERIFICATION="INDEPENDENT_VERIFICATION"; HUMAN_AUTHORIZATION_REQUIRED="HUMAN_AUTHORIZATION_REQUIRED"
@dataclass(frozen=True)
class OversightDecision:
 risk_level:str;action:OversightAction;automatic_irreversible_authorization:bool;reason:str
def oversight_for(risk_level,sensitive_action=False,degraded=False):
 level=str(getattr(risk_level,"value",risk_level)).upper()
 if degraded and sensitive_action:return OversightDecision(level,OversightAction.INDEPENDENT_VERIFICATION,False,"System degraded; independent verification required.")
 if level=="CRITICAL":return OversightDecision(level,OversightAction.HUMAN_AUTHORIZATION_REQUIRED,False,"Critical interactions cannot authorize sensitive action solely from AI output.")
 if level=="HIGH":return OversightDecision(level,OversightAction.INDEPENDENT_VERIFICATION,not sensitive_action,"Independent verification required for high risk.")
 if level=="MEDIUM":return OversightDecision(level,OversightAction.MONITOR,not sensitive_action,"Monitor the interaction.")
 return OversightDecision(level,OversightAction.AUTOMATED_NORMAL,not sensitive_action,"Normal automated processing is allowed by policy.")
def can_proceed(risk_level,sensitive_action,human_authorized=False,independently_verified=False,degraded=False):
 rule=oversight_for(risk_level,sensitive_action,degraded)
 if not sensitive_action:return True
 if rule.action==OversightAction.HUMAN_AUTHORIZATION_REQUIRED:return bool(human_authorized and independently_verified)
 if rule.action==OversightAction.INDEPENDENT_VERIFICATION:return bool(independently_verified)
 return True
