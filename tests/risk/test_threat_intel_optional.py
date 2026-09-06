from src.risk.engine import RiskEngine
def test_threat_intelligence_disabled_by_default(risk_config):
 base=RiskEngine(risk_config).evaluate({"synthetic_probability":.2})
 enriched=RiskEngine(risk_config).evaluate({"synthetic_probability":.2,"threat_intelligence_risk":100})
 assert enriched["signal_breakdown"]["threat_intelligence"]==0 and enriched["risk_score"]==base["risk_score"]
