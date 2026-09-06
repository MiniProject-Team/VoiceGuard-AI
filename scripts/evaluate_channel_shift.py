import argparse,csv,json
from phase12_common import *
def main():
 p=argparse.ArgumentParser();p.add_argument("--config",default=ROOT/"configs/advanced_evaluation.yaml");a=p.parse_args();minimum=config(a.config)["evaluation"]["minimum_group_samples"]
 with (ROOT/"reports/phase9/robustness_results.csv").open(encoding="utf-8") as f:result=[dict(r) for r in csv.DictReader(f)]
 for r in result:r["phase12_status"]="INSUFFICIENT DATA" if int(r["sample_count"])<minimum else "OK"
 payload={"conditions":result,"attack_channel_matrix":{"UNKNOWN_SYNTHETIC":{r["condition"]:{"sample_count":int(r["sample_count"]),"f1":None if int(r["sample_count"])<minimum else float(r["f1"]),"status":r["phase12_status"]} for r in result}},"note":"Conditions are benign simulations inherited from Phase 9; all groups are below minimum sample size."};write("channel_shift.json",payload);print(json.dumps(payload,indent=2))
if __name__=="__main__":main()
