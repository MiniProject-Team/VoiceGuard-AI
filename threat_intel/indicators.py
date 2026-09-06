from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class ThreatIndicator:
    name: str; severity: str; rationale: str; proof_of_attack: bool=False

def derive_indicators(event: dict) -> list[dict]:
    p=event.get("synthetic_probability"); sim=event.get("speaker_similarity"); out=[]
    if isinstance(p,(int,float)) and p>=.8: out.append(ThreatIndicator("high_synthetic_probability","HIGH","Detector score exceeds the configured research threshold."))
    if isinstance(p,(int,float)) and p>=.8 and isinstance(sim,(int,float)) and sim>=.75: out.append(ThreatIndicator("synthetic_high_match","CRITICAL","Possible cloned voice matching an enrolled identity."))
    if event.get("channel_changed"): out.append(ThreatIndicator("unexpected_channel_change","MEDIUM","Observed channel metadata changed unexpectedly."))
    if event.get("repeat_count",0)>=3: out.append(ThreatIndicator("rapid_session_repetition","MEDIUM","Repeated pseudonymous-source activity in the configured window."))
    if event.get("detector_disagreement"): out.append(ThreatIndicator("detector_disagreement","MEDIUM","Available defensive signals disagree."))
    if event.get("uncertainty")=="HIGH_UNCERTAINTY": out.append(ThreatIndicator("uncertainty_spike","MEDIUM","Detector output is close to its decision boundary."))
    return [asdict(x) for x in out]
