from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
os.environ.setdefault("MPLBACKEND","Agg");import matplotlib.pyplot as plt
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml
from src.risk import RiskEngine,RiskInput
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--config",default=str(ROOT/"configs/risk_engine.yaml"));a=p.parse_args();config=load_yaml(a.config)
    scenarios={"genuine_normal":RiskInput(.05,.9,speaker_verified=True,claimed_identity=True,call_origin="known",contact_match=True,transaction_amount=1000,privileged_action=False,historical_fraud_indicator=False,new_device=False,unusual_time=False,location_anomaly=False),"different_speaker":RiskInput(.1,.1,speaker_verified=False,claimed_identity=True,call_origin="known",contact_match=True,transaction_amount=1000,privileged_action=False,historical_fraud_indicator=False,new_device=False,unusual_time=False,location_anomaly=False),"ai_clone":RiskInput(.95,.92,speaker_verified=True,claimed_identity=True,call_origin="known",contact_match=True,transaction_amount=1000,privileged_action=False,historical_fraud_indicator=False,new_device=False,unusual_time=False,location_anomaly=False),"high_value":RiskInput(.45,.9,speaker_verified=True,claimed_identity=True,call_origin="known",contact_match=True,transaction_amount=250000,privileged_action=False,historical_fraud_indicator=False,new_device=False,unusual_time=False,location_anomaly=False),"unknown_caller":RiskInput(.3,None,speaker_verified=None,claimed_identity=False,call_origin="unknown"),"multiple_indicators":RiskInput(.98,.1,speaker_verified=False,claimed_identity=True,call_origin="unknown",contact_match=False,transaction_amount=500000,privileged_action=True,historical_fraud_indicator=True,new_device=True,unusual_time=True,location_anomaly=True)}
    rows=[]
    for name,value in scenarios.items():
        result=RiskEngine(config).evaluate(value);rows.append({"scenario":name,"simulation":True,"risk_score":result["risk_score"],"risk_level":result["risk_level"],"decision":result["decision"],**{f"signal_{k}":v for k,v in result["signal_breakdown"].items()}});print(f"{name}: {result['risk_score']:.2f} {result['risk_level']} {result['decision']}")
    frame=pd.DataFrame(rows);report=ROOT/"reports/phase5";report.mkdir(parents=True,exist_ok=True);frame.to_csv(report/"risk_scenarios.csv",index=False)
    frame.plot.bar(x="scenario",y="risk_score",legend=False);plt.ylabel("Simulated risk score");plt.tight_layout();plt.savefig(report/"risk_distribution.png");plt.close()
    columns=[c for c in frame if c.startswith("signal_") and c!="signal_total"];frame.set_index("scenario")[columns].plot.bar(stacked=True);plt.ylabel("Score contribution");plt.tight_layout();plt.savefig(report/"signal_contribution.png");plt.close();print("SIMULATION / DEMONSTRATION — not real-world performance")
if __name__=="__main__":main()
