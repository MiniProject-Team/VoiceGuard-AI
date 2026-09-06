"""Timestamped segment generation from incoming chunks."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .audio_buffer import AudioBuffer
from .vad import EnergyVAD
@dataclass
class RealtimeSegment:
    session_id:str;segment_id:int;start_time:float;end_time:float;audio:np.ndarray;speech_ratio:float
class RealtimeSegmenter:
    def __init__(self,session_id:str,buffer:AudioBuffer,vad:EnergyVAD):self.session_id=session_id;self.buffer=buffer;self.vad=vad;self.count=0
    def add_chunk(self,chunk:np.ndarray):
        self.buffer.append(chunk)
        for audio,start in self.buffer.windows():
            segment=RealtimeSegment(self.session_id,self.count,start/self.buffer.sample_rate,(start+len(audio))/self.buffer.sample_rate,audio,self.vad.speech_ratio(audio));self.count+=1;yield segment
