import pytest
from src.speaker.similarity import cosine_similarity
def test_known_vectors():
    assert cosine_similarity([1,0],[1,0])==pytest.approx(1)
    assert cosine_similarity([1,0],[0,1])==pytest.approx(0)
    assert cosine_similarity([1,0],[-1,0])==pytest.approx(-1)
