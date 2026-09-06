import numpy as np
from src.realtime.audio_buffer import AudioBuffer
from src.realtime.segmenter import RealtimeSegmenter
from src.realtime.vad import EnergyVAD
def test_size_hop_and_timestamps():
    segmenter=RealtimeSegmenter("s",AudioBuffer(10,3000,1000),EnergyVAD(10,.01,100));items=list(segmenter.add_chunk(np.ones(40)));assert len(items)==2 and len(items[0].audio)==30 and items[1].start_time==1 and items[1].end_time==4
