"""Failure-tolerant Phase 3/4/5 orchestration with preloaded model adapters."""
from __future__ import annotations
from time import perf_counter
from typing import Any,Callable
from src.risk.schema import RiskInput
class SegmentProcessor:
    def __init__(self,synthetic_detector:Callable, speaker_verifier:Callable, risk_engine:Any):self.synthetic_detector=synthetic_detector;self.speaker_verifier=speaker_verifier;self.risk_engine=risk_engine
    def process(self,segment:Any,speaker_id:str|None,context:dict[str,Any])->dict[str,Any]:
        errors=[];p3_start=perf_counter();synthetic=None;classification=None;p3_status="ok"
        try:
            response=self.synthetic_detector(segment.audio);synthetic=response.get("synthetic_probability");classification=response.get("classification")
        except Exception as exc:p3_status="unavailable";errors.append(f"phase3:{type(exc).__name__}")
        p3_time=perf_counter()-p3_start;p4_start=perf_counter();similarity=None;verified=None;p4_status="unavailable"
        if speaker_id:
            try:
                response=self.speaker_verifier(speaker_id,segment.audio);similarity=response.get("similarity");verified=response.get("verified");p4_status=response.get("status","ok")
            except Exception as exc:p4_status="unavailable";errors.append(f"phase4:{type(exc).__name__}")
        p4_time=perf_counter()-p4_start;p5_start=perf_counter()
        payload={**context,"synthetic_probability":synthetic,"speaker_similarity":similarity,"speaker_verified":verified,"speaker_verification_status":p4_status,"claimed_identity":speaker_id is not None,"session_id":segment.session_id}
        risk=self.risk_engine.evaluate(RiskInput.from_dict(payload));p5_time=perf_counter()-p5_start
        return {"synthetic_probability":synthetic,"classification":classification,"synthetic_detection_status":p3_status,"speaker_similarity":similarity,"speaker_verified":verified,"speaker_verification_status":p4_status,"risk":risk,"errors":errors,"phase3_time":p3_time,"phase4_time":p4_time,"phase5_time":p5_time}
    def warmup(self,sample_rate=16000,duration_seconds=1.)->dict[str,str]:
        import numpy as np
        dummy=np.zeros(round(sample_rate*duration_seconds),dtype=np.float32);result={}
        for name,function,args in (("phase3",self.synthetic_detector,(dummy,)),):
            try:function(*args);result[name]="ok"
            except Exception:result[name]="unavailable"
        return result
