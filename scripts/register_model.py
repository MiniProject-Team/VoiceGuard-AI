from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mlops.model_registry import ModelRegistry
from mlops.model_metadata import load_json,dataset_metadata
from security.integrity import sha256_file
from src.models.readiness import reject_debug_or_random_artifact
def main():
 p=argparse.ArgumentParser();p.add_argument("--type",required=True,choices=["synthetic_detector","speaker_verifier","risk_engine"]);p.add_argument("--path",required=True);p.add_argument("--version");a=p.parse_args();target=(ROOT/a.path).resolve();registry=ROOT/f"models/registry/{a.type}/registry.json"
 if a.type=="synthetic_detector":
  info=load_json(target/"model_config.json",{}); training_path=target/"training_config.yaml"
  if not training_path.is_file(): raise FileNotFoundError(f"Synthetic detector registration requires {training_path}")
  cfg=__import__('yaml').safe_load(training_path.read_text()); reject_debug_or_random_artifact(cfg,info)
  if not a.version or "debug" in a.version.lower(): raise ValueError("Synthetic detector registration requires a new non-debug immutable version, e.g. v4-trained.")
  if not info.get("test_metrics"): raise ValueError("Synthetic detector registration requires held-out test metrics in model_config.json.")
  version=a.version;metadata={"dataset_version":dataset_metadata(ROOT/"data/metadata/train.csv")["dataset_version"],"validation_metrics":info.get("validation_metrics"),"test_metrics":info.get("test_metrics"),"threshold":info.get("threshold"),"config_hash":sha256_file(training_path)};name=info.get("configured_base_model","wav2vec2")
 elif a.type=="speaker_verifier":version=a.version or "v1";threshold=load_json(ROOT/"models/speaker_verification/calibrated_threshold.json",{});metadata={"embedding_dimension":192,"sample_rate":16000,"threshold":threshold.get("threshold"),"validation_eer":load_json(ROOT/"reports/phase4/eer.json",{}).get("eer"),"config_hash":sha256_file(ROOT/"configs/speaker_verification.yaml")};name="SpeechBrain ECAPA-TDNN"
 else:version=a.version or "phase5-v1";cfg=__import__('yaml').safe_load((ROOT/"configs/risk_engine.yaml").read_text());metadata={"weights":cfg["signals"],"thresholds":cfg["risk"]["thresholds"],"rules":cfg["rules"],"config_hash":sha256_file(ROOT/"configs/risk_engine.yaml")};name="VoiceGuard Risk Engine"
 record=ModelRegistry(registry).register(a.type,name,version,target,metadata);print(json.dumps(record,indent=2))
if __name__=="__main__":main()
