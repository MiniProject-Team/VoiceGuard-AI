import numpy as np
from src.realtime.audio_buffer import AudioBuffer
def test_chunk_window_overlap_and_limit():
    buffer=AudioBuffer(10,3000,1000,max_windows=2);buffer.append(np.arange(20));assert list(buffer.windows())==[];buffer.append(np.arange(20,40));windows=list(buffer.windows());assert len(windows)==2 and windows[0][1]==0 and windows[1][1]==10
    np.testing.assert_array_equal(windows[0][0][10:],windows[1][0][:20])
    buffer.append(np.ones(100));assert buffer.buffered_samples<=buffer.max_samples
