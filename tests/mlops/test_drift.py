import numpy as np
from mlops.drift import detect_drift
def test_drift_states():
 rng=np.random.default_rng(1);reference=rng.normal(0,1,1000);assert detect_drift(reference,reference.copy())["state"]=="NO_DRIFT";assert detect_drift(reference,rng.normal(.25,1,1000))["state"] in {"POSSIBLE_DRIFT","SIGNIFICANT_DRIFT"};assert detect_drift(reference,rng.normal(3,1,1000))["state"]=="SIGNIFICANT_DRIFT";assert detect_drift([1],[1])["state"]=="INSUFFICIENT_DATA"
