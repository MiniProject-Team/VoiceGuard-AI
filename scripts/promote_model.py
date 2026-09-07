from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mlops.model_registry import ModelRegistry
def main():
 p=argparse.ArgumentParser();p.add_argument("--type",required=True);p.add_argument("--model-id",required=True);p.add_argument("--validation-approved",action="store_true");p.add_argument("--technical-validation",action="store_true");p.add_argument("--security-checks",action="store_true");p.add_argument("--privacy-checks",action="store_true");p.add_argument("--known-limitations",action="store_true");p.add_argument("--governance-approval",action="store_true");a=p.parse_args();registry=ModelRegistry(ROOT/f"models/registry/{a.type}/registry.json");item=registry.get(a.model_id)
 if item["status"]=="CANDIDATE": checks={"tests_pass":a.validation_approved,"metrics_available":a.validation_approved,"config_valid":a.validation_approved,"model_loads":a.validation_approved,"latency_acceptable":a.validation_approved,"no_leakage_warning":a.validation_approved,"artifact_hash":registry.validate_hash(a.model_id)}
 elif item["status"]=="STAGING": checks={"technical_validation":a.technical_validation,"security_checks":a.security_checks,"privacy_checks":a.privacy_checks,"known_limitations":a.known_limitations,"governance_approval":a.governance_approval}
 else: raise ValueError(f"Only CANDIDATE or STAGING models can be promoted; current status is {item['status']}")
 print(json.dumps(registry.promote(a.model_id,checks),indent=2))
if __name__=="__main__":main()
