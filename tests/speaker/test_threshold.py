import numpy as np,pandas as pd,pytest
from src.speaker.threshold import calculate_eer,select_threshold
def test_eer_and_validation_selection():
    trials=pd.DataFrame({"trial_type":["genuine","genuine","impostor","impostor"],"similarity":[.9,.8,.2,.1]})
    threshold,analysis=select_threshold(trials);assert 0<=threshold<=1 and not analysis.empty
    eer,_=calculate_eer(np.array([1,1,0,0]),np.array([.9,.8,.2,.1]));assert eer==pytest.approx(0)
