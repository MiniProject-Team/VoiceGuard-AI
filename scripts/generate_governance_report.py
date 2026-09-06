from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from governance.roles import ROLE_PERMISSIONS
OUT=ROOT/"reports/phase13/governance_report.json"
def main():
 data={"scope":"Compliance-ready governance controls; no certification or legal-compliance claim.","roles":{r.value:sorted(p.value for p in ps) for r,ps in ROLE_PERMISSIONS.items()},"metrics":{"overrides":0,"policy_changes":0,"exceptions":0,"model_approvals":0,"model_rejections":0,"retention_deletions":0},"note":"Metrics contain actual records only; this fresh report has no supplied event log."};OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(data,indent=2),encoding="utf-8");print(f"Governance report generated: {OUT}");return data
if __name__=="__main__":main()
