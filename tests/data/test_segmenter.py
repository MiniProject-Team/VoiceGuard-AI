import numpy as np
from src.data.segmenter import segment_audio

def test_correct_count_and_overlap():
    segments = segment_audio(np.arange(100, dtype=np.float32), 10, 5, 2.5)
    assert len(segments) == 3
    assert [s.start_time for s in segments] == [0, 2.5, 5]
    np.testing.assert_array_equal(segments[0].audio[25:], segments[1].audio[:25])

def test_short_audio_padding_and_metadata():
    result = segment_audio(np.ones(20, dtype=np.float32), 10, 5, 2.5)
    assert len(result) == 1 and len(result[0].audio) == 50
    assert result[0].padding_applied and result[0].duration == 2

def test_short_audio_skip():
    assert segment_audio(np.ones(20), 10, 5, 2.5, "skip") == []
