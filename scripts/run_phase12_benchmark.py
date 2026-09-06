import csv,json,time,uuid
from datetime import datetime,timezone
from phase12_common import *
from advanced_eval.benchmark import binary_metrics,grouped_metrics,write_benchmark
from advanced_eval.uncertainty import analyze_uncertainty
from threat_intel.indicators import derive_indicators
def main():
 c=config(ROOT/"configs/advanced_evaluation.yaml");minimum=c["evaluation"]["minimum_group_samples"];data=rows();start=time.perf_counter();
 for r in data: r["uncertainty"]=analyze_uncertainty(r["score"])["level"];derive_indicators({"synthetic_probability":r["score"],"uncertainty":r["uncertainty"]})
 overhead=(time.perf_counter()-start)*1000/max(1,len(data));m=binary_metrics(data)
 available=[{"test":"genuine_and_known_synthetic","condition":"clean","sample_count":len(data),"accuracy":m["accuracy"],"precision":m["precision"],"recall":m["recall"],"F1":m["f1"],"FNR":m["fnr"],"latency":"NOT MEASURED","notes":"INSUFFICIENT DATA"}]
 for test in ("human_impostor","unseen_synthetic","replay","telephone_simulation","noise","low_bitrate","unknown_language"):available.append({"test":test,"condition":"UNKNOWN","sample_count":0,"accuracy":None,"precision":None,"recall":None,"F1":None,"FNR":None,"latency":"NOT TESTED","notes":"NOT TESTED / no labelled data"})
 OUT.mkdir(parents=True,exist_ok=True);write_benchmark(OUT/"benchmark.csv",available)
 grouped={f:grouped_metrics(data,f,minimum) for f in ("attack_family","channel_type","language")};fn=sorted([x for x in grouped["attack_family"] if x["fnr"] is not None],key=lambda x:x["fnr"],reverse=True);fp=sorted([x for x in grouped["attack_family"] if x["fpr"] is not None],key=lambda x:x["fpr"],reverse=True)
 manifest={"experiment_id":f"EXPERIMENT_{uuid.uuid4().hex[:12].upper()}","dataset_version":"phase3-test-3-sample-debug","model_version":"v3-debug","config_hash":cfg_hash(ROOT/"configs/advanced_evaluation.yaml"),"seed":c["evaluation"]["seed"],"timestamp":datetime.now(timezone.utc).isoformat(),"metrics":m,"minimum_group_samples":minimum,"status":"INSUFFICIENT DATA","added_runtime_overhead_ms_per_event":overhead};write("experiment_manifest.json",manifest);write("benchmark_summary.json",{"grouped":grouped,"highest_fnr_conditions":fn,"highest_fpr_conditions":fp,"overhead_ms_per_event":overhead,"warning":"Do not interpret tiny groups as research evidence."});print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
