def threat_intelligence_risk(indicators, config):
    if not config.get("enabled",False): return {"enabled":False,"risk":0.0,"matched":[]}
    signals=config.get("signals",{});matched=[x for x in indicators if x in signals]
    return {"enabled":True,"risk":min(100.0,sum(float(signals[x].get("weight",0)) for x in matched)),"matched":matched}

def policy_recommendation(campaign: dict):
    elevated=campaign.get("event_count",0)>=3 and campaign.get("risk_distribution",{}).get("CRITICAL",0)>=2
    return {"recommendation":"INCREASE_STEP_UP_VERIFICATION" if elevated else "MAINTAIN_CURRENT_POLICY","reason":"Elevated rate of critical synthetic-voice events" if elevated else "No sufficiently supported elevated campaign signal","automatic_change_applied":False}

def incident_summary(event: dict):
    risk=float(event.get("risk_score",0)); context=event.get("context",{}) if isinstance(event.get("context",{}),dict) else {}
    priority="P1_CRITICAL" if risk>=80 or (risk>=60 and context.get("sensitive")) else "P2_HIGH" if risk>=60 else "P3_MODERATE" if risk>=30 else "P4_INFORMATIONAL"
    keys=("session_id","risk_level","synthetic_probability","speaker_similarity","context","attack_family","uncertainty","recommended_action")
    return {**{k:event.get(k,"UNKNOWN") for k in keys},"priority":priority}
