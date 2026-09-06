from __future__ import annotations
import numpy as np,pandas as pd
from .channel_tests import add_noise,telephone_bandlimited,low_volume,mild_reverb,codec_like,speed_perturbation
from .multilingual import binary_metrics
TRANSFORMS={"clean":lambda x,s:x,"telephone_bandlimited":telephone_bandlimited,"low_volume":lambda x,s:low_volume(x),"reverberant":mild_reverb,"codec_like":lambda x,s:codec_like(x),"speed_perturbation":lambda x,s:speed_perturbation(x)}
def evaluate_conditions(samples:list[tuple[str,int,np.ndarray]],detector,sample_rate=16000,snr_levels=(20,10,5),minimum_samples=10)->list[dict]:
    rows=[];conditions=list(TRANSFORMS)+[f"noise_{snr}db" for snr in snr_levels]
    for condition in conditions:
        predictions=[]
        for audio_id,label,audio in samples:
            transformed=add_noise(audio,float(condition.split('_')[1][:-2])) if condition.startswith("noise_") else TRANSFORMS[condition](audio,sample_rate);prob=detector(transformed)["synthetic_probability"];predictions.append({"audio_id":audio_id,"true_label":label,"probability_fake":prob})
        metrics=binary_metrics(pd.DataFrame(predictions));count=metrics.pop("count");status="MEASURED CLEAN" if condition=="clean" else "SIMULATED CONDITION";status=status if count>=minimum_samples else status+" - INSUFFICIENT DATA";rows.append({"condition":condition,"status":status,"sample_count":count,**metrics})
    return rows
def cross_dataset_evaluation(frame:pd.DataFrame)->dict:
    if "source_dataset" not in frame or frame.source_dataset.dropna().nunique()<2:return {"status":"NOT TESTED","reason":"Fewer than two labeled source datasets are available."}
    return {"status":"SUPPORTED","datasets":sorted(frame.source_dataset.dropna().unique().tolist())}
def held_out_generator_evaluation(frame:pd.DataFrame)->dict:
    if "synthesis_method" not in frame or frame.synthesis_method.dropna().nunique()<2:return {"status":"NOT TESTED","reason":"Generator metadata is unavailable or has fewer than two methods."}
    return {"status":"SUPPORTED","generators":sorted(frame.synthesis_method.dropna().unique().tolist())}
def alert_fatigue(events:list[dict])->dict:
    alerts=[event for event in events if event.get("event_type")=="AlertTriggered"];sessions={event.get("session_id") for event in events if event.get("session_id")};keys=[(x.get("session_id"),x.get("risk_level"),x.get("decision")) for x in alerts];return {"alerts":len(alerts),"sessions":len(sessions),"alerts_per_session":len(alerts)/len(sessions) if sessions else 0,"duplicate_alerts":len(keys)-len(set(keys)),"critical_alerts":sum(x.get("severity")=="critical" for x in alerts)}
def temporal_stability(scores:list[tuple[float,str]],duration_minutes:float)->dict:
    transitions=sum(a[1]!=b[1] for a,b in zip(scores,scores[1:]));return {"transitions":transitions,"transitions_per_minute":transitions/duration_minutes if duration_minutes>0 else None}
def session_decision(rows:list[dict])->dict:
    scores=[float(row.get("risk_score") or 0) for row in rows];critical=sum(row.get("risk_level")=="CRITICAL" for row in rows);return {"status":"MEASURED" if rows else "INSUFFICIENT DATA","segments":len(rows),"maximum_risk":max(scores) if scores else None,"mean_risk":sum(scores)/len(scores) if scores else None,"critical_segments":critical}
