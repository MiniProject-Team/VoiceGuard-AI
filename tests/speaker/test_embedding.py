import numpy as np,torch
from src.speaker.embedding import extract_embedding_from_waveform,normalize_embedding
class MockModel:
    def encode_batch(self,waveform): return torch.tensor([[[3.,4.,0.]]])
def test_output_shape_and_normalization():
    result=extract_embedding_from_waveform(np.ones(16000,dtype=np.float32),16000,MockModel())
    assert result.shape==(3,) and np.linalg.norm(result)==np.float32(1)
def test_normalize_embedding(): np.testing.assert_allclose(normalize_embedding([3,4]),[.6,.8])
