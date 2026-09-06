import numpy as np
from src.realtime.audio_stream import AudioStream
from src.realtime.pipeline import RealtimePipeline
from src.realtime.processor import SegmentProcessor
from src.realtime.session import CallSession
from src.risk import RiskEngine
class Stream(AudioStream):
    def __init__(self,chunks):self.chunks=chunks;self.stopped=False
    def start(self):pass
    def read(self):yield from self.chunks
    def stop(self):self.stopped=True
def _config():return {"audio":{"sample_rate":10},"analysis":{"window_duration_ms":3000,"hop_duration_ms":1000},"vad":{"enabled":True,"energy_threshold":.1,"frame_duration_ms":100,"minimum_speech_ratio":.4},"runtime":{"failure_escalation_count":2},"alerts":{"enabled":True,"cooldown_seconds":30,"minimum_level":"HIGH"},"output":{"jsonl":True}}
def test_pipeline_output_files_and_empty_stream(tmp_path,risk_config):
    processor=SegmentProcessor(lambda x:{"synthetic_probability":.1},lambda s,x:{"similarity":.9,"verified":True},RiskEngine(risk_config));stream=Stream([np.ones(10),np.ones(20)]);pipeline=RealtimePipeline(stream,processor,CallSession("s","a",{}),_config(),tmp_path);events=[];pipeline.on_result(events.append);results=pipeline.run();assert len(results)==1 and results[0]["status"]=="ok" and stream.stopped
    assert (tmp_path/"latency.csv").exists() and (tmp_path/"realtime_results.jsonl").exists() and (tmp_path/"session_summary.json").exists()
    empty=RealtimePipeline(Stream([]),processor,CallSession("e"),_config(),tmp_path/"empty");assert empty.run()==[]
def test_silence_and_system_degraded(tmp_path,risk_config):
    okay=SegmentProcessor(lambda x:{"synthetic_probability":.1},lambda s,x:{},RiskEngine(risk_config));silence=RealtimePipeline(Stream([np.zeros(30)]),okay,CallSession("z"),_config(),tmp_path/"silent").run();assert silence[0]["status"]=="insufficient_speech"
    failed=SegmentProcessor(lambda x:(_ for _ in()).throw(RuntimeError()),lambda s,x:(_ for _ in()).throw(RuntimeError()),RiskEngine(risk_config));pipeline=RealtimePipeline(Stream([np.ones(40)]),failed,CallSession("f","x"),_config(),tmp_path/"fail");results=pipeline.run();assert results[-1]["status"]=="SYSTEM_DEGRADED" and results[-1]["decision"]=="STEP_UP_VERIFICATION"
