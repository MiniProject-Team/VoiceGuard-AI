from __future__ import annotations
import argparse,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml,resolve_path
from src.speaker.embedding import extract_embedding,load_speaker_model

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--metadata",required=True);p.add_argument("--config",default=str(ROOT/"configs/speaker_verification.yaml"));a=p.parse_args();cp=Path(a.config).resolve();cfg=load_yaml(cp);base=cp.parent.parent
    frame=pd.read_csv(a.metadata);model=load_speaker_model(cfg["model"]["name"],savedir=base/"models/speaker_verification/model_cache");cache=resolve_path(cfg["paths"]["embedding_dir"],base)/"cache"
    for path in frame.file_path: extract_embedding(path,model,cfg["model"]["name"],cfg["audio"],cache,cfg["preprocessing_version"],cfg["verification"]["normalize_embeddings"])
    print(f"Cached embeddings for {len(frame)} files; values are not displayed.")
if __name__=="__main__":main()
