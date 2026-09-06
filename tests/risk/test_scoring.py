import math,pytest
from src.risk.scoring import normalize_probability,normalize_similarity,speaker_mismatch
def test_probability_normalization_and_missing():
    assert normalize_probability(None) is None and normalize_probability(-2)==0 and normalize_probability(2)==1
    with pytest.raises(ValueError):normalize_probability(math.nan)
def test_similarity_range_and_calibrated_mismatch():
    assert normalize_similarity(-1)==0 and normalize_similarity(1)==1 and speaker_mismatch(1,None)==0
    assert speaker_mismatch(None,.8)==.8
