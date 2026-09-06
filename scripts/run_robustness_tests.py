from __future__ import annotations
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd,numpy as np,soundfile as sf,yaml
from src.realtime.adapters import SyntheticDetectorAdapter
from evaluation.robustness import evaluate_conditions,cross_dataset_evaluation,held_out_generator_evaluation
from evaluation.calibration import calibration_metrics,threshold_stress
from evaluation.latency_tests import summarize,real_time_factor
from evaluation.report import write_csv,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",default="configs/evaluation.yaml");p.add_argument("--skip-inference",action="store_true");a=p.parse_args();cfg=yaml.safe_load((ROOT/a.config).read_text());pred=pd.read_csv(ROOT/cfg["paths"]["predictions"]);out=ROOT/cfg["paths"]["output_dir"];out.mkdir(parents=True,exist_ok=True)
 cal=calibration_metrics(pred.true_label,pred.probability_fake,int(cfg["calibration"]["bins"]));cal["threshold_stress"]=threshold_stress(pred.true_label,pred.probability_fake,cfg["thresholds"]["synthetic"]);write_json(out/"calibration.json",cal)
 false_pos=pred[(pred.true_label==0)&(pred.probability_fake>=pred.threshold)].copy();false_neg=pred[(pred.true_label==1)&(pred.probability_fake<pred.threshold)].copy();columns=[c for c in ["audio_path","language","source_dataset","probability_fake"] if c in pred];false_pos[columns].to_csv(out/"false_positive_analysis.csv",index=False);false_neg[columns].to_csv(out/"false_negative_analysis.csv",index=False)
 if a.skip_inference:rows=[{"condition":name,"status":"NOT TESTED - inference skipped","sample_count":0} for name in cfg["robustness"]["conditions"]];latency={"status":"NOT TESTED"}
 else:
  model=SyntheticDetectorAdapter(ROOT/"models/best_model");samples=[]
  for row in pred.head(int(cfg["robustness"]["sample_limit"])).itertuples():
   audio,rate=sf.read(row.audio_path,dtype="float32");
   if rate==16000:samples.append((Path(row.audio_path).name,int(row.true_label),np.asarray(audio,dtype=np.float32)))
  started=time.perf_counter();rows=evaluate_conditions(samples,model,16000,cfg["robustness"]["snr_db"]);elapsed=time.perf_counter()-started;duration=sum(len(x[2])/16000 for x in samples)*len(rows);latency={"phase3_robustness_batch":summarize([elapsed]),"audio_duration_seconds":duration,"rtf":real_time_factor(elapsed,duration),"device":str(model.device)}
 generalization={"cross_dataset":cross_dataset_evaluation(pred),"held_out_generator":held_out_generator_evaluation(pred),"replay":"NOT TESTED - replay metadata unavailable"};write_csv(out/"robustness_results.csv",rows);write_json(out/"latency_summary.json",latency);write_json(out/"generalization_summary.json",generalization);print(json.dumps({"conditions":rows,"latency":latency,"generalization":generalization},indent=2))
if __name__=="__main__":main()
