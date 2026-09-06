"""Sequential near-real-time stream orchestration and structured event output."""
from __future__ import annotations
import json,logging
from pathlib import Path
from time import perf_counter
from typing import Callable
from .alerts import AlertManager
from .audio_buffer import AudioBuffer
from .metrics import LatencyTracker
from .segmenter import RealtimeSegmenter
from .session import CallSession
from .vad import EnergyVAD
LOGGER=logging.getLogger(__name__)
class RealtimePipeline:
    def __init__(self,stream,processor,session:CallSession,config:dict,report_dir:str|Path):
        self.stream,self.processor,self.session,self.config,self.report_dir=stream,processor,session,config,Path(report_dir);self.callbacks=[];self.latency=LatencyTracker();self.failure_count=0
        self.buffer=AudioBuffer(int(config["audio"]["sample_rate"]),int(config["analysis"]["window_duration_ms"]),int(config["analysis"]["hop_duration_ms"]));self.vad=EnergyVAD(int(config["audio"]["sample_rate"]),float(config["vad"]["energy_threshold"]),int(config["vad"]["frame_duration_ms"]));self.segmenter=RealtimeSegmenter(session.session_id,self.buffer,self.vad);self.alerts=AlertManager(config["alerts"]["enabled"],float(config["alerts"]["cooldown_seconds"]),config["alerts"]["minimum_level"],self._emit)
    def on_result(self,callback:Callable[[dict],None])->None:self.callbacks.append(callback)
    def _emit(self,event:dict)->None:
        for callback in self.callbacks:callback(event)
    def _write(self,result:dict)->None:
        if self.config["output"].get("jsonl"):
            self.report_dir.mkdir(parents=True,exist_ok=True)
            with (self.report_dir/"realtime_results.jsonl").open("a",encoding="utf-8") as stream:stream.write(json.dumps(result)+"\n")
    def run(self)->list[dict]:
        results=[];sample_rate=int(self.config["audio"]["sample_rate"]);minimum=float(self.config["vad"]["minimum_speech_ratio"]);call_samples=0
        try:
            with self.stream:
                for chunk in self.stream.read():
                    call_samples+=len(chunk);self._emit({"event_type":"AudioChunkReceived","session_id":self.session.session_id,"num_samples":len(chunk)})
                    for segment in self.segmenter.add_chunk(chunk):
                        self._emit({"event_type":"AudioSegmentReady","session_id":segment.session_id,"segment_id":segment.segment_id,"start_time":segment.start_time,"end_time":segment.end_time,"speech_ratio":segment.speech_ratio})
                        if self.config["vad"]["enabled"] and segment.speech_ratio<minimum:
                            result={"event_type":"AnalysisCompleted","session_id":segment.session_id,"segment_id":segment.segment_id,"start_time":segment.start_time,"end_time":segment.end_time,"speech_ratio":segment.speech_ratio,"status":"insufficient_speech","synthetic_probability":None,"speaker_similarity":None,"risk_score":None,"risk_level":"UNKNOWN","decision":"NO_ANALYSIS","recommended_action":"Wait for sufficient speech.","alert":False};results.append(result);self._write(result);self._emit(result);continue
                        started=perf_counter();analysis=self.processor.process(segment,self.session.speaker_id,self.session.context);total=perf_counter()-started;risk=analysis["risk"]
                        self.failure_count=self.failure_count+1 if analysis["errors"] else 0;degraded=self.failure_count>=int(self.config["runtime"]["failure_escalation_count"])
                        result={"event_type":"RiskUpdated","session_id":segment.session_id,"segment_id":segment.segment_id,"start_time":segment.start_time,"end_time":segment.end_time,"speech_ratio":segment.speech_ratio,"status":"SYSTEM_DEGRADED" if degraded else "ok","synthetic_probability":analysis["synthetic_probability"],"synthetic_detection_status":analysis["synthetic_detection_status"],"speaker_similarity":analysis["speaker_similarity"],"speaker_verified":analysis["speaker_verified"],"speaker_verification_status":analysis["speaker_verification_status"],"risk_score":risk["risk_score"],"risk_level":risk["risk_level"],"decision":"STEP_UP_VERIFICATION" if degraded else risk["decision"],"recommended_action":"Require independent verification because security models are unavailable." if degraded else risk["recommended_action"],"reasons":risk["reasons"],"signal_breakdown":risk["signal_breakdown"],"errors":analysis["errors"],"processing_time":total,"audio_duration":segment.end_time-segment.start_time,"rtf":total/(segment.end_time-segment.start_time)}
                        state=self.session.record(result);result["session_state"]=state;alert=self.alerts.consider(result);result["alert"]=alert is not None
                        if alert and alert["severity"]=="critical":self.session.critical_alerts+=1
                        self.latency.add(session_id=segment.session_id,segment_id=segment.segment_id,audio_duration=result["audio_duration"],processing_time=total,rtf=result["rtf"],phase3_time=analysis["phase3_time"],phase4_time=analysis["phase4_time"],phase5_time=analysis["phase5_time"],total_time=total)
                        results.append(result);self._write(result);self._emit(result);LOGGER.info("session=%s segment=%s time=%.4f risk=%s",segment.session_id,segment.segment_id,total,result["risk_level"])
        except KeyboardInterrupt:LOGGER.info("Session interrupted")
        finally:
            self.buffer.clear();self.report_dir.mkdir(parents=True,exist_ok=True);self.latency.save(self.report_dir);self.last_summary=self.session.summary(call_samples/sample_rate);(self.report_dir/"session_summary.json").write_text(json.dumps(self.last_summary,indent=2),encoding="utf-8")
        return results
