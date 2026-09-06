"""Speaker enrollment and verification (independent of deepfake detection)."""
from .verifier import SpeakerVerifier, verify_speaker
__all__ = ["SpeakerVerifier", "verify_speaker"]
