import math

def analyze_uncertainty(probability,threshold=.5,medium_margin=.2,high_margin=.08,calibrated=False):
    if probability is None:return {"level":"HIGH_UNCERTAINTY","classification":"uncertain","distance":None,"entropy":None,"calibrated":calibrated}
    p=max(0.,min(1.,float(probability)));distance=abs(p-threshold);entropy=-(p*math.log2(p)+(1-p)*math.log2(1-p)) if p not in (0,1) else 0.
    level="HIGH_UNCERTAINTY" if distance<=high_margin else "MEDIUM_UNCERTAINTY" if distance<=medium_margin else "LOW_UNCERTAINTY"
    classification="uncertain" if level=="HIGH_UNCERTAINTY" else "high certainty fake" if p>=threshold else "high certainty real"
    return {"level":level,"classification":classification,"distance":distance,"entropy":entropy,"calibrated":calibrated,"caution":"Probability distance and entropy are proxies, not guaranteed certainty."}
