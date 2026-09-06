import csv,json
from phase12_common import *
from advanced_eval.disagreement import disagreement_profile
from advanced_eval.uncertainty import analyze_uncertainty
def main():
 data=[]
 with (ROOT/"reports/phase6/realtime_results.jsonl").open(encoding="utf-8") as f:
  for i,line in enumerate(f,1):
   x=json.loads(line);u=analyze_uncertainty(x.get("synthetic_probability"));d=disagreement_profile(x.get("synthetic_probability"),x.get("speaker_similarity"),x.get("risk_score"));data.append({"session/sample ID":f"ATTACK_SCENARIO_{i:03d}","synthetic score":x.get("synthetic_probability"),"speaker similarity":x.get("speaker_similarity"),"risk":x.get("risk_score"),"uncertainty":u["level"],"result":d["result"]})
 OUT.mkdir(parents=True,exist_ok=True)
 with (OUT/"detector_disagreement.csv").open("w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
 counts={k:sum(x["uncertainty"]==k for x in data) for k in ("LOW_UNCERTAINTY","MEDIUM_UNCERTAINTY","HIGH_UNCERTAINTY")};write("uncertainty_summary.json",{"counts":counts,"sample_count":len(data),"warning":"INSUFFICIENT DATA"});print(json.dumps(counts,indent=2))
if __name__=="__main__":main()
