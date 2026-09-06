from collections import defaultdict
import csv, math

def binary_metrics(rows, threshold=.5):
    pairs=[(int(r["label"]),float(r["score"])) for r in rows if r.get("label") not in (None,"") and r.get("score") not in (None,"")]
    if not pairs:return {k:None for k in ("accuracy","precision","recall","f1","roc_auc","fnr","fpr")}
    tp=sum(y==1 and s>=threshold for y,s in pairs);tn=sum(y==0 and s<threshold for y,s in pairs);fp=sum(y==0 and s>=threshold for y,s in pairs);fn=sum(y==1 and s<threshold for y,s in pairs)
    precision=tp/(tp+fp) if tp+fp else 0.;recall=tp/(tp+fn) if tp+fn else 0.;f1=2*precision*recall/(precision+recall) if precision+recall else 0.
    pos=[s for y,s in pairs if y];neg=[s for y,s in pairs if not y];auc=None
    if pos and neg:auc=sum(1 if p>n else .5 if p==n else 0 for p in pos for n in neg)/(len(pos)*len(neg))
    return {"accuracy":(tp+tn)/len(pairs),"precision":precision,"recall":recall,"f1":f1,"roc_auc":auc,"fnr":fn/(tp+fn) if tp+fn else 0.,"fpr":fp/(tn+fp) if tn+fp else 0.}

def grouped_metrics(rows, field, minimum=20, threshold=.5):
    groups=defaultdict(list)
    for r in rows:groups[str(r.get(field) or "UNKNOWN")].append(r)
    return [{"group":name,"sample_count":len(items),"status":"OK" if len(items)>=minimum else "INSUFFICIENT DATA",**(binary_metrics(items,threshold) if len(items)>=minimum else {k:None for k in ("accuracy","precision","recall","f1","roc_auc","fnr","fpr")})} for name,items in sorted(groups.items())]

def write_benchmark(path, records):
    fields=["test","condition","sample_count","accuracy","precision","recall","F1","FNR","latency","notes"]
    with open(path,"w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:r.get(k) for k in fields} for r in records])
