from __future__ import annotations
import json
from pathlib import Path
from security.integrity import config_hash,sha256_file
def directory_hash(path:str|Path)->str:
 target=Path(path)
 if target.is_file():return sha256_file(target)
 files=sorted(p for p in target.rglob("*") if p.is_file());return config_hash(files)
def dataset_metadata(path:str|Path)->dict:
 import pandas as pd
 target=Path(path);frame=pd.read_csv(target);labels=frame.get("label_name",frame.get("label"));return {"dataset_id":target.stem,"dataset_version":sha256_file(target)[:12],"number_of_samples":len(frame),"real_count":int((labels.astype(str).str.lower().isin(["real","0"])).sum()),"fake_count":int((labels.astype(str).str.lower().isin(["fake","1"])).sum()),"languages":sorted(frame.get("language",pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),"source_datasets":sorted(frame.get("source_dataset",pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),"metadata_hash":sha256_file(target)}
def load_json(path:str|Path,default=None):
 try:return json.loads(Path(path).read_text(encoding="utf-8"))
 except FileNotFoundError:return default
