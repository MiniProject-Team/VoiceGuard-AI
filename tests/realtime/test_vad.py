import numpy as np
from src.realtime.vad import EnergyVAD
def test_silence_speech_and_ratio():
    vad=EnergyVAD(100,.1,100);assert vad.speech_ratio(np.zeros(100))==0 and vad.is_speech(np.ones(100),.5)
    assert vad.speech_ratio(np.r_[np.ones(50),np.zeros(50)])==.5
