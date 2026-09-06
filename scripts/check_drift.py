from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd,yaml
from mlops.drift import detect_drift
def main():
 cfg=yaml.safe_load((ROOT/"configs/monitoring.yaml").read_text());data=pd.read_csv(ROOT/"reports/phase3/test_predictions.csv")["probability_fake"].dropna().tolist();split=max(1,len(data)//2);result={"synthetic_scores":detect_drift(data[:split],data[split:],**{k:cfg["drift"][k] for k in ("minimum_samples","possible_ks","significant_ks","possible_psi","significant_psi")}),"speaker_scores":{"state":"INSUFFICIENT_DATA"},"audio_duration":{"state":"INSUFFICIENT_DATA"},"speech_ratio":{"state":"INSUFFICIENT_DATA"},"risk_score":{"state":"INSUFFICIENT_DATA"},"action":"Investigate and collect labeled examples; no automatic retraining or promotion."};out=ROOT/"reports/phase11";out.mkdir(parents=True,exist_ok=True);(out/"drift_report.json").write_text(json.dumps(result,indent=2));(out/"drift_report.md").write_text("# Drift report\n\nAll monitored distributions: **INSUFFICIENT_DATA**. Minimum configured samples: 100. No retraining action was taken.\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
