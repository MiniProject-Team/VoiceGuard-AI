"""Deterministic, explainable, stateful-optional risk orchestration."""
from __future__ import annotations
from collections import deque
from datetime import datetime, timezone
from typing import Any
from .context import evaluate_context
from .decision import decision_for, risk_level
from .rules import apply_rules
from .schema import RiskInput
from .scoring import clamp, normalize_probability, normalize_similarity, speaker_mismatch, weighted_contribution

class TemporalAggregator:
    def __init__(self, config: dict[str,Any]):
        self.config=config;self.scores=deque(maxlen=int(config["window_size"]));self.levels=deque(maxlen=int(config["window_size"]));self.ema=None;self.high_state=False
    def update(self,score:float,level:str)->dict[str,Any]:
        self.scores.append(score);self.levels.append(level);method=self.config["method"]
        if method=="mean":aggregated=sum(self.scores)/len(self.scores)
        elif method=="maximum":aggregated=max(self.scores)
        elif method=="ema":
            alpha=float(self.config["ema_alpha"]);self.ema=score if self.ema is None else alpha*score+(1-alpha)*self.ema;aggregated=self.ema
        else:raise ValueError("temporal.method must be mean, maximum, or ema")
        if not self.high_state and aggregated>=float(self.config["high_entry_score"]):self.high_state=True
        elif self.high_state and aggregated<float(self.config["high_exit_score"]):self.high_state=False
        high_count=sum(item in {"HIGH","CRITICAL"} for item in self.levels);escalate=high_count>=int(self.config["escalation_threshold"])
        return {"method":method,"aggregated_score":float(aggregated),"window_count":len(self.scores),"high_risk_count":high_count,"persistent_escalation":escalate,"hysteresis_high_state":self.high_state}

class RiskEngine:
    def __init__(self,config:dict[str,Any]):
        self.config=config;self.temporal=TemporalAggregator(config["temporal"]) if config["temporal"].get("enabled") else None
    def evaluate(self,value:RiskInput|dict[str,Any])->dict[str,Any]:
        item=RiskInput.from_dict(value) if isinstance(value,dict) else value;weights=self.config["signals"];reasons=[];missing=[];available=[]
        synthetic=normalize_probability(item.synthetic_probability)
        if synthetic is None:missing.append("synthetic_probability")
        else:
            available.append("synthetic_probability")
            if synthetic>=float(self.config["rules"]["synthetic_high_threshold"]):reasons.append("Strong synthetic-speech indicators were reported.")
        similarity=normalize_similarity(item.speaker_similarity,float(self.config["speaker_similarity"]["minimum"]),float(self.config["speaker_similarity"]["maximum"]))
        mismatch=speaker_mismatch(item.speaker_similarity,item.speaker_mismatch_probability,float(self.config["speaker_similarity"]["minimum"]),float(self.config["speaker_similarity"]["maximum"]))
        if mismatch is None:
            missing.extend(["speaker_similarity","speaker_verified"] if item.speaker_verified is None else ["speaker_similarity"])
            reasons.append("Speaker verification could not be performed because no usable reference result is available.")
        else:available.append("speaker_mismatch_probability" if item.speaker_mismatch_probability is not None else "speaker_similarity")
        context_score,context_reasons,context_missing=evaluate_context(item,self.config["context"]);reasons.extend(context_reasons);missing.extend(context_missing)
        context_fields=("call_origin","contact_match","transaction_amount","privileged_action","historical_fraud_indicator","unusual_time","new_device","location_anomaly")
        available.extend(field for field in context_fields if getattr(item,field) is not None)
        if item.speaker_verified is not None: available.append("speaker_verified")
        breakdown={"synthetic_voice":weighted_contribution(synthetic,weights["synthetic_voice"]["weight"],weights["synthetic_voice"]["enabled"]),
                   "speaker_mismatch":weighted_contribution(mismatch,weights["speaker_mismatch"]["weight"],weights["speaker_mismatch"]["enabled"]),
                   "context":min(context_score,float(weights["contextual"]["weight"])*100) if weights["contextual"]["enabled"] else 0.}
        threat_cfg=weights.get("threat_intelligence",{"enabled":False,"weight":0})
        breakdown["threat_intelligence"]=weighted_contribution(normalize_probability(None if item.threat_intelligence_risk is None else float(item.threat_intelligence_risk)/100),threat_cfg.get("weight",0),threat_cfg.get("enabled",False))
        if item.threat_intelligence_risk is not None:available.append("threat_intelligence_risk")
        bonuses,rule_reasons=apply_rules(item,synthetic,similarity,self.config["rules"]);breakdown.update(bonuses);reasons.extend(rule_reasons)
        minimum,maximum=float(self.config["risk"]["score_range"]["min"]),float(self.config["risk"]["score_range"]["max"]);score=clamp(sum(breakdown.values()),minimum,maximum);breakdown["total"]=score
        level=risk_level(score,self.config["risk"]["thresholds"]);decision,action=decision_for(level,self.config["decisions"])
        temporal=self.temporal.update(score,level) if self.temporal else None
        if temporal and temporal["persistent_escalation"] and level in {"LOW","MEDIUM"}:decision="STEP_UP_VERIFICATION";action=self.config["decisions"]["high"]["recommended_action"];reasons.append("Risk remained high across multiple recent segments.")
        signals={key:value for key,value in item.to_dict().items() if key not in {"session_id"} and value is not None}
        result={"risk_score":round(score,4),"risk_level":level,"decision":decision,"recommended_action":action,"reasons":list(dict.fromkeys(reasons)),"signals":signals,"signal_breakdown":{k:round(v,4) for k,v in breakdown.items()},"available_signals":sorted(set(available)),"missing_signals":sorted(set(missing)),"temporal":temporal,"configuration_version":self.config["version"],"engine_version":self.config["engine_version"]}
        result["audit_event"]={"event_type":"voice_risk_assessment","timestamp":datetime.now(timezone.utc).isoformat(),"session_id":item.session_id,"risk_score":result["risk_score"],"risk_level":level,"decision":decision,"configuration_version":self.config["version"],"engine_version":self.config["engine_version"],"input_signal_summary":signals,"risk_breakdown":result["signal_breakdown"]}
        return result
