from __future__ import annotations
import argparse,json,logging,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.models.utils import load_yaml,resolve_path
from src.realtime.adapters import MockSpeakerVerifier,MockSyntheticDetector,SpeakerVerifierAdapter,SyntheticDetectorAdapter
from src.realtime.audio_stream import FileAudioStream
from src.realtime.pipeline import RealtimePipeline
from src.realtime.processor import SegmentProcessor
from src.realtime.session import CallSession
from src.risk.engine import RiskEngine
def display(event):
    if event.get("event_type")!="RiskUpdated":return
    print(f"Segment {event['segment_id']} {event['start_time']:.1f}-{event['end_time']:.1f}s | speech {event['speech_ratio']:.0%} | synthetic {event['synthetic_probability']} | similarity {event['speaker_similarity']} | risk {event['risk_score']}/100 {event['risk_level']} | {event['decision']}")
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--audio",required=True);p.add_argument("--speaker-id");p.add_argument("--session-id",default="CALL_DEMO_001");p.add_argument("--simulate-realtime",action="store_true");p.add_argument("--mock-models",action="store_true");p.add_argument("--config",default=str(ROOT/"configs/realtime.yaml"));p.add_argument("--context-json");a=p.parse_args();cfg=load_yaml(a.config);logging.basicConfig(level=getattr(logging,cfg["logging"]["level"]));dependencies=cfg["dependencies"]
    risk=RiskEngine(load_yaml(resolve_path(dependencies["risk_config"],ROOT)))
    synthetic=MockSyntheticDetector() if a.mock_models else SyntheticDetectorAdapter(resolve_path(dependencies["phase3_model"],ROOT));speaker=MockSpeakerVerifier() if a.mock_models else SpeakerVerifierAdapter(resolve_path(dependencies["phase4_config"],ROOT),ROOT)
    processor=SegmentProcessor(synthetic,speaker,risk);context=json.loads(Path(a.context_json).read_text()) if a.context_json else {"call_origin":"known","contact_match":True,"transaction_amount":0,"privileged_action":False,"historical_fraud_indicator":False,"new_device":False,"unusual_time":False,"location_anomaly":False}
    session=CallSession(a.session_id,a.speaker_id,context,int(cfg["history"]["max_segments"]));stream=FileAudioStream(a.audio,int(cfg["audio"]["sample_rate"]),int(cfg["stream"]["chunk_duration_ms"]),a.simulate_realtime);pipeline=RealtimePipeline(stream,processor,session,cfg,resolve_path(cfg["output"]["report_dir"],ROOT));pipeline.on_result(display)
    if cfg["runtime"].get("warmup"):print("Warm-up:",processor.warmup(int(cfg["audio"]["sample_rate"])))
    results=pipeline.run();print(json.dumps(pipeline.last_summary,indent=2));print(f"Emitted {len(results)} segment results. This is near-real-time, not telecom-grade hard real-time.")
if __name__=="__main__":main()
