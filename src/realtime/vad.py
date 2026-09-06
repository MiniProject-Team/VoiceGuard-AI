"""Lightweight configurable energy-based speech activity baseline."""
from __future__ import annotations
import numpy as np
class EnergyVAD:
    def __init__(self,sample_rate=16000,energy_threshold=.005,frame_duration_ms=20):self.sample_rate=sample_rate;self.threshold=energy_threshold;self.frame_samples=max(1,round(sample_rate*frame_duration_ms/1000))
    def speech_ratio(self,audio:np.ndarray)->float:
        value=np.asarray(audio,dtype=np.float32).reshape(-1)
        if not value.size:return 0.
        ratios=[]
        for start in range(0,len(value),self.frame_samples):
            frame=value[start:start+self.frame_samples];ratios.append(float(np.sqrt(np.mean(frame*frame)))>=self.threshold)
        return float(np.mean(ratios))
    def is_speech(self,audio:np.ndarray,minimum_ratio=.4)->bool:return self.speech_ratio(audio)>=minimum_ratio
