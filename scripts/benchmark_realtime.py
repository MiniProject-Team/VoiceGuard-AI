from __future__ import annotations
import argparse,json,sys,time
from pathlib import Path
import numpy as np,pandas as pd,soundfile as sf
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml,resolve_path
from src.realtime.adapters import MockSpeakerVerifier,MockSyntheticDetector
from src.realtime.processor import SegmentProcessor
from src.realtime.segmenter import RealtimeSegment
from src.risk.engine import RiskEngine
def main():
    p=argparse.ArgumentParser();p.add_argument("--audio",required=True);p.add_argument("--config",default=str(ROOT/"configs/realtime.yaml"));a=p.parse_args();cfg=load_yaml(a.config);audio,sr=sf.read(a.audio,dtype="float32");audio=np.asarray(audio).reshape(-1);target=round(int(cfg["audio"]["sample_rate"])*int(cfg["analysis"]["window_duration_ms"])/1000);audio=np.resize(audio,target).astype(np.float32);risk=RiskEngine(load_yaml(resolve_path(cfg["dependencies"]["risk_config"],ROOT)));processor=SegmentProcessor(MockSyntheticDetector(.6),MockSpeakerVerifier(.8),risk);rows=[]
    for count in (10,50,100):
        times=[]
        for index in range(count):
            segment=RealtimeSegment("BENCHMARK",index,0,len(audio)/16000,audio,1.);started=time.perf_counter();processor.process(segment,"demo_speaker",{});times.append(time.perf_counter()-started)
        values=np.array(times);rows.append({"segments":count,"mean":values.mean(),"median":np.median(values),"p95":np.percentile(values,95),"maximum":values.max(),"mean_rtf":values.mean()/(len(audio)/16000)})
    report=resolve_path(cfg["output"]["report_dir"],ROOT);report.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(report/"benchmark.csv",index=False);print(json.dumps(rows,indent=2));print("Benchmark uses preloaded deterministic adapters; model loading is excluded.")
if __name__=="__main__":main()
