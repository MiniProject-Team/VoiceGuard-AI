import numpy as np
import soundfile as sf
from src.data.audio_utils import convert_to_mono, load_audio, normalize_audio, resample_audio

def test_convert_to_mono():
    stereo = np.array([[1, -1], [.5, .5]], dtype=np.float32)
    np.testing.assert_allclose(convert_to_mono(stereo), [0, .5])

def test_resampling():
    result = resample_audio(np.zeros(8000, dtype=np.float32), 8000, 16000)
    assert abs(len(result) - 16000) <= 1 and result.dtype == np.float32

def test_normalization_is_conservative():
    quiet = np.array([-.2, .2], dtype=np.float32)
    np.testing.assert_array_equal(normalize_audio(quiet), quiet)
    assert np.max(np.abs(normalize_audio(np.array([-2., 2.])))) <= .99

def test_loading(tmp_path):
    path = tmp_path / "tone.wav"; sf.write(path, np.zeros(160), 16000)
    audio, sr = load_audio(path)
    assert sr == 16000 and len(audio) == 160
