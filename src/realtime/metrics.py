"""Latency row collection and summary persistence."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
class LatencyTracker:
    def __init__(self):self.rows=[]
    def add(self,**row):self.rows.append(row)
    def save(self,report_dir:str|Path)->dict:
        out=Path(report_dir);out.mkdir(parents=True,exist_ok=True);frame=pd.DataFrame(self.rows);frame.to_csv(out/"latency.csv",index=False)
        values=frame["total_time"].to_numpy() if not frame.empty else np.array([]);summary={"count":len(values),"mean":float(np.mean(values)) if len(values) else None,"median":float(np.median(values)) if len(values) else None,"p95":float(np.percentile(values,95)) if len(values) else None,"maximum":float(np.max(values)) if len(values) else None,"mean_rtf":float(frame.rtf.mean()) if not frame.empty else None};(out/"latency_summary.json").write_text(json.dumps(summary,indent=2));return summary
