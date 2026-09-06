from __future__ import annotations
import importlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import yaml
from security.privacy import assert_privacy_defaults
def run_checks():
 required={"Preprocessing config":"configs/preprocessing.yaml","Phase 3 model":"models/best_model/model.pt","Phase 4 model":"models/speaker_verification/model_cache/embedding_model.ckpt","Risk config":"configs/risk_engine.yaml","Realtime config":"configs/realtime.yaml","API config":"configs/api.yaml","Privacy config":"configs/privacy.yaml","Security config":"configs/security.yaml","Evaluation config":"configs/evaluation.yaml","Integration config":"configs/integration.yaml","Frontend":"frontend/package.json"};checks={name:(ROOT/path).is_file() for name,path in required.items()}
 try:importlib.import_module("api.main");checks["Backend import"]=True
 except Exception:checks["Backend import"]=False
 try:
  privacy=yaml.safe_load((ROOT/"configs/privacy.yaml").read_text());assert_privacy_defaults(privacy);checks["Privacy defaults"]=True
 except Exception:checks["Privacy defaults"]=False
 try:
  risk=yaml.safe_load((ROOT/"configs/risk_engine.yaml").read_text());t=risk["risk"]["thresholds"];checks["Risk thresholds"]=0<=t["low_max"]<t["medium_max"]<t["high_max"]<t["critical_min"]<=100
 except Exception:checks["Risk thresholds"]=False
 try:
  api=yaml.safe_load((ROOT/"configs/api.yaml").read_text());checks["API port"]=1<=int(api["server"]["port"])<=65535
 except Exception:checks["API port"]=False
 checks["Environment"]="VOICEGUARD_PSEUDONYM_KEY" in os.environ
 return checks
def main():
 checks=run_checks();print("VOICEGUARD PROJECT VALIDATION\n");[print(f"{name:<30} {'PASS' if value else 'WARN' if name=='Environment' else 'FAIL'}") for name,value in checks.items()];ready=all(v for k,v in checks.items() if k!="Environment");print(f"\nPROJECT STATUS: {'READY' if ready else 'NOT READY'}");return 0 if ready else 1
if __name__=="__main__":raise SystemExit(main())
