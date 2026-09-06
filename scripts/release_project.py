from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mlops.release import release_manifest
def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest-only",action="store_true");a=p.parse_args();validation=json.loads((ROOT/"reports/final/final_validation.json").read_text());models={};
 for kind in ("synthetic_detector","speaker_verifier","risk_engine"):
  path=ROOT/f"models/registry/{kind}/registry.json"
  if path.exists():models[kind]=[{"model_id":x["model_id"],"version":x["model_version"],"status":x["status"]} for x in json.loads(path.read_text())["models"]]
 if validation["status"]!="SIH DEMO READY" and not a.manifest_only:raise SystemExit("Release blocked: final validation is not SIH DEMO READY. Use --manifest-only for an auditable prototype manifest.")
 manifest=release_manifest(ROOT,"0.11.0",validation["status"],models);out=ROOT/"reports/phase11";out.mkdir(parents=True,exist_ok=True);(out/"release_manifest.json").write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2));
if __name__=="__main__":main()
