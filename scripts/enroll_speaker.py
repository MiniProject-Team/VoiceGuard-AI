from __future__ import annotations
import argparse, logging, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml, resolve_path
from src.speaker.embedding import extract_embedding, load_speaker_model
from src.speaker.enrollment import enroll_speaker

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--speaker-id",required=True); p.add_argument("--audio",action="append",default=[]); p.add_argument("--audio-dir",type=Path); p.add_argument("--output"); p.add_argument("--config",default=str(ROOT/"configs/speaker_verification.yaml")); a=p.parse_args()
    logging.basicConfig(level=logging.INFO); cp=Path(a.config).resolve(); cfg=load_yaml(cp); base=cp.parent.parent; paths=[Path(item) for item in a.audio]
    if a.audio_dir: paths.extend(sorted(path for path in a.audio_dir.rglob("*") if path.suffix.lower() in {".wav",".flac",".mp3",".ogg"}))
    output=Path(a.output) if a.output else resolve_path(cfg["paths"]["embedding_dir"],base); model_dir=base/"models/speaker_verification/model_cache"
    model=load_speaker_model(cfg["model"]["name"],savedir=model_dir)
    extractor=lambda path: extract_embedding(path,model,cfg["model"]["name"],cfg["audio"],output/"cache",cfg["preprocessing_version"],cfg["verification"]["normalize_embeddings"])
    metadata=enroll_speaker(a.speaker_id,paths,extractor,output,{"model_name":cfg["model"]["name"],"model_version":cfg["model"]["version"],"sample_rate":cfg["audio"]["sample_rate"],"preprocessing_version":cfg["preprocessing_version"]},int(cfg["enrollment"]["minimum_reference_files"]))
    print(f"Enrolled {metadata['speaker_id']} from {metadata['number_of_reference_files']} references; embedding dimension {metadata['embedding_dimension']}. Embedding values are not displayed.")
if __name__=="__main__": main()
