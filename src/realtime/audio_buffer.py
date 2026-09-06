"""Bounded overlapping analysis-window buffer."""
from __future__ import annotations
from collections import deque
import numpy as np
class AudioBuffer:
    def __init__(self,sample_rate:int,window_duration_ms:int,hop_duration_ms:int,max_windows:int=3):
        self.sample_rate=sample_rate;self.window_samples=round(sample_rate*window_duration_ms/1000);self.hop_samples=round(sample_rate*hop_duration_ms/1000);self.max_samples=max(self.window_samples,self.window_samples+self.hop_samples*max_windows);self._audio=np.empty(0,dtype=np.float32);self.consumed_samples=0
        if self.window_samples<=0 or self.hop_samples<=0:raise ValueError("Window and hop must be positive")
    def append(self,chunk:np.ndarray)->None:
        value=np.asarray(chunk,dtype=np.float32).reshape(-1)
        if value.size:self._audio=np.concatenate((self._audio,value))
        if len(self._audio)>self.max_samples:
            excess=len(self._audio)-self.max_samples;self._audio=self._audio[excess:];self.consumed_samples+=excess
    def windows(self):
        while len(self._audio)>=self.window_samples:
            start=self.consumed_samples;window=self._audio[:self.window_samples].copy();self._audio=self._audio[self.hop_samples:];self.consumed_samples+=self.hop_samples;yield window,start
    @property
    def buffered_samples(self)->int:return len(self._audio)
    def clear(self)->None:self._audio=np.empty(0,dtype=np.float32)
