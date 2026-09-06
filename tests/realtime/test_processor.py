from types import SimpleNamespace
from src.realtime.processor import SegmentProcessor
from src.risk import RiskEngine
def test_orchestration_and_failures(risk_config):
    segment=SimpleNamespace(audio=[1,2],session_id="s");processor=SegmentProcessor(lambda x:{"synthetic_probability":.9},lambda s,x:{"similarity":.9,"verified":True,"status":"ok"},RiskEngine(risk_config));result=processor.process(segment,"a",{});assert result["synthetic_probability"]==.9 and result["risk"]["risk_level"] in {"HIGH","CRITICAL"}
    failed=SegmentProcessor(lambda x:(_ for _ in()).throw(RuntimeError()),lambda s,x:(_ for _ in()).throw(RuntimeError()),RiskEngine(risk_config)).process(segment,"a",{});assert failed["synthetic_probability"] is None and len(failed["errors"])==2
