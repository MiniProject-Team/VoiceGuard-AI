from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml,resolve_path
from src.realtime.adapters import MockSpeakerVerifier,MockSyntheticDetector
from src.realtime.audio_stream import MicrophoneAudioStream
from src.realtime.pipeline import RealtimePipeline
from src.realtime.processor import SegmentProcessor
from src.realtime.session import CallSession
from src.risk.engine import RiskEngine
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",choices=["microphone"],default="microphone");p.add_argument("--config",default=str(ROOT/"configs/realtime.yaml"));a=p.parse_args();cfg=load_yaml(a.config);risk=RiskEngine(load_yaml(resolve_path(cfg["dependencies"]["risk_config"],ROOT)));stream=MicrophoneAudioStream(int(cfg["audio"]["sample_rate"]),int(cfg["stream"]["chunk_duration_ms"]));pipeline=RealtimePipeline(stream,SegmentProcessor(MockSyntheticDetector(),MockSpeakerVerifier(),risk),CallSession("MIC_DEMO"),cfg,resolve_path(cfg["output"]["report_dir"],ROOT));pipeline.on_result(lambda x:print(x) if x.get("event_type")=="RiskUpdated" else None);pipeline.run()
if __name__=="__main__":main()
