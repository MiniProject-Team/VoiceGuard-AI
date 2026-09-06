from __future__ import annotations
import numpy as np
def summarize(values)->dict:
    data=np.asarray(values,dtype=float)
    if not len(data):return {"status":"NOT TESTED","count":0}
    return {"status":"MEASURED","count":len(data),"mean":float(data.mean()),"median":float(np.median(data)),"p95":float(np.percentile(data,95)),"max":float(data.max())}
def real_time_factor(processing_time:float,audio_duration:float)->float:return processing_time/audio_duration if audio_duration>0 else float("inf")
