from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mlops.model_registry import ModelRegistry
def main():
 p=argparse.ArgumentParser();p.add_argument("--type",required=True);p.add_argument("--model-id",required=True);p.add_argument("--validation-approved",action="store_true");p.add_argument("--override",action="store_true");a=p.parse_args();registry=ModelRegistry(ROOT/f"models/registry/{a.type}/registry.json");checks={"tests_pass":a.validation_approved,"metrics_available":a.validation_approved,"config_valid":a.validation_approved,"model_loads":a.validation_approved,"latency_acceptable":a.validation_approved,"no_leakage_warning":a.validation_approved,"artifact_hash":registry.validate_hash(a.model_id)};print(json.dumps(registry.promote(a.model_id,checks,a.override),indent=2))
if __name__=="__main__":main()
