import numpy as np

def safe_perturb(audio, kind, seed=26104):
    """Non-optimized, bounded transforms for defensive evaluation only."""
    x=np.asarray(audio,dtype=np.float32)
    if kind=="small_gain":return np.clip(x*.9,-1,1)
    if kind=="small_timing_shift":return np.roll(x,min(80,len(x)))
    if kind=="background_noise":return np.clip(x+np.random.default_rng(seed).normal(0,.002,len(x)),-1,1).astype(np.float32)
    if kind=="frequency_filter":return np.convolve(x,np.ones(3,dtype=np.float32)/3,mode="same").astype(np.float32)
    raise ValueError("Unsupported safe perturbation")
