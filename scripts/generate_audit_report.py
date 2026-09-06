from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import yaml
from security.audit import verify_audit_chain
from evaluation.report import write_json
def main():
 cfg=yaml.safe_load((ROOT/"configs/security.yaml").read_text());result=verify_audit_chain(ROOT/cfg["audit"]["path"]);write_json(ROOT/"reports/phase9/audit_integrity_report.json",result);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
