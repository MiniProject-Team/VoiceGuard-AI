from __future__ import annotations
import numpy as np
from sklearn.metrics import brier_score_loss
def calibration_metrics(labels,probabilities,bins:int=10)->dict:
    y=np.asarray(labels,dtype=int);p=np.clip(np.asarray(probabilities,dtype=float),0,1)
    if not len(y):return {"status":"INSUFFICIENT DATA","count":0}
    edges=np.linspace(0,1,bins+1);ece=0.;curve=[]
    for low,high in zip(edges[:-1],edges[1:]):
        mask=(p>=low)&((p<high) if high<1 else (p<=high))
        if not mask.any():continue
        confidence=float(p[mask].mean());accuracy=float(y[mask].mean());count=int(mask.sum());ece+=count/len(y)*abs(confidence-accuracy);curve.append({"lower":low,"upper":high,"count":count,"mean_probability":confidence,"observed_rate":accuracy})
    return {"status":"MEASURED","count":len(y),"brier_score":float(brier_score_loss(y,p)),"expected_calibration_error":float(ece),"reliability_curve":curve,"warning":"Softmax probabilities are not assumed to be perfectly calibrated."}
def threshold_stress(labels,probabilities,thresholds)->list[dict]:
    y=np.asarray(labels,dtype=int);p=np.asarray(probabilities,dtype=float);rows=[]
    for threshold in thresholds:
        pred=p>=threshold;tp=int(((pred==1)&(y==1)).sum());tn=int(((pred==0)&(y==0)).sum());fp=int(((pred==1)&(y==0)).sum());fn=int(((pred==0)&(y==1)).sum());rows.append({"threshold":threshold,"fpr":fp/(fp+tn) if fp+tn else None,"fnr":fn/(fn+tp) if fn+tp else None,"alert_rate":float(pred.mean()) if len(pred) else None})
    return rows
