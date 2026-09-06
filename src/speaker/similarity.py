"""Embedding similarity functions without decision policy."""
from __future__ import annotations
import numpy as np

def cosine_similarity(reference_embedding: np.ndarray, test_embedding: np.ndarray) -> float:
    a, b = np.asarray(reference_embedding, dtype=np.float32).reshape(-1), np.asarray(test_embedding, dtype=np.float32).reshape(-1)
    if a.shape != b.shape: raise ValueError(f"Embedding shapes differ: {a.shape} vs {b.shape}")
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0: raise ValueError("Cosine similarity is undefined for a zero vector")
    return float(np.dot(a, b) / denominator)
