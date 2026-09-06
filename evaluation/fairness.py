from __future__ import annotations
def performance_disparity(rows:list[dict],metric="f1")->dict:
    measured=[row for row in rows if row.get("status")=="MEASURED" and row.get(metric) is not None]
    if len(measured)<2:return {"status":"INSUFFICIENT DATA","groups_measured":len(measured),"note":"At least two legitimate metadata groups are required."}
    best=max(measured,key=lambda x:x[metric]);worst=min(measured,key=lambda x:x[metric]);return {"status":"MEASURED","best_group":best.get("language"),"best_f1":best[metric],"best_count":best["count"],"worst_group":worst.get("language"),"worst_f1":worst[metric],"worst_count":worst["count"],"gap":best[metric]-worst[metric]}
