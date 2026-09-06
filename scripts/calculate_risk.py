from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml
from src.risk import RiskEngine,RiskInput
from src.risk.explanations import format_assessment
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--config",default=str(ROOT/"configs/risk_engine.yaml"));a=p.parse_args();engine=RiskEngine(load_yaml(a.config));value=RiskInput.from_dict(json.loads(Path(a.input).read_text(encoding="utf-8")));result=engine.evaluate(value);print(format_assessment(result));print("\nJSON:\n"+json.dumps(result,indent=2))
if __name__=="__main__":main()
