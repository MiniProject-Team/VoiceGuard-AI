from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml,resolve_path
from src.speaker.embedding import extract_embedding_from_waveform,load_speaker_model
from src.speaker.verifier import SpeakerVerifier

def main()->None:
    p=argparse.ArgumentParser(); p.add_argument("--speaker-id",required=True); p.add_argument("--audio",required=True); p.add_argument("--config",default=str(ROOT/"configs/speaker_verification.yaml")); a=p.parse_args()
    cp=Path(a.config).resolve(); cfg=load_yaml(cp); base=cp.parent.parent; threshold=cfg["verification"]["threshold"]; calibrated=resolve_path(cfg["paths"]["calibrated_threshold"],base)
    if threshold is None and calibrated.exists(): threshold=json.loads(calibrated.read_text())["threshold"]
    model=load_speaker_model(cfg["model"]["name"],savedir=base/"models/speaker_verification/model_cache")
    extractor=lambda waveform,sr: extract_embedding_from_waveform(waveform,sr,model,int(cfg["audio"]["sample_rate"]),cfg["verification"]["normalize_embeddings"])
    verifier=SpeakerVerifier(resolve_path(cfg["paths"]["embedding_dir"],base),extractor,cfg["audio"],threshold,cfg["verification"]["aggregation"]); result=verifier.verify(a.speaker_id,a.audio)
    print("Speaker Verification\n---------------------\n"); print(f"Speaker ID: {a.speaker_id}\nSimilarity: {result['similarity']}\nThreshold: {result['threshold']}\nStatus: {result['status']}")
    if result["verified"] is not None: print(f"Decision: {'VERIFIED' if result['verified'] else 'NOT VERIFIED'}")
    if result.get("reason"): print(f"Reason: {result['reason']}")
    print("A match is not proof of identity and may be vulnerable to replay or cloning.")
if __name__=="__main__":main()
