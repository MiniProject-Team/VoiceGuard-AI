from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import yaml
from monitoring.metrics import MetricsCollector
from monitoring.alerts import operational_alerts
def main():
 collector=MetricsCollector();source=ROOT/"reports/phase6/realtime_results.jsonl"
 if source.exists():
  for line in source.read_text().splitlines():
   row=json.loads(line)
   if row.get("risk_score") is not None:collector.record(latency=row.get("processing_time",0),rtf=row.get("rtf"),synthetic=row.get("synthetic_probability"),speaker=row.get("speaker_similarity"),risk=row.get("risk_score"),level=row.get("risk_level","UNKNOWN"),alert=row.get("alert",False),degraded=row.get("status")=="SYSTEM_DEGRADED")
 cfg=yaml.safe_load((ROOT/"configs/monitoring.yaml").read_text());summary=collector.summary();result={"metrics":summary,"operational_alerts":operational_alerts(summary,cfg),"security_alerts":"tracked separately","source":"privacy-safe Phase 6 structured results"};out=ROOT/"reports/phase11";out.mkdir(parents=True,exist_ok=True);(out/"monitoring_report.json").write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=="__main__":main()
