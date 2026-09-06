from src.risk import RiskEngine,RiskInput
def test_clone_is_high_and_explainable(risk_config):
    result=RiskEngine(risk_config).evaluate(RiskInput(synthetic_probability=.95,speaker_similarity=.95,speaker_verified=True,call_origin="known"))
    assert result["risk_level"] in {"HIGH","CRITICAL"} and any("synthetic" in reason.lower() and "matches" in reason.lower() for reason in result["reasons"])
    assert 0<=result["risk_score"]<=100 and result["signal_breakdown"]["total"]==result["risk_score"]
def test_missing_data_and_unknown_speaker(risk_config):
    result=RiskEngine(risk_config).evaluate(RiskInput(synthetic_probability=.2));assert "speaker_similarity" in result["missing_signals"] and result["risk_score"]>=0
def test_score_cap(risk_config):
    value=RiskInput(1,-1,speaker_verified=False,claimed_identity=True,call_origin="suspicious",contact_match=False,transaction_amount=1e9,privileged_action=True,historical_fraud_indicator=True,new_device=True,unusual_time=True,location_anomaly=True)
    assert RiskEngine(risk_config).evaluate(value)["risk_score"]==100
def test_temporal_escalation_and_hysteresis(risk_config):
    engine=RiskEngine(risk_config);high=RiskInput(1,-1,speaker_verified=False);low=RiskInput(0,1,speaker_verified=True)
    for _ in range(3):engine.evaluate(high)
    result=engine.evaluate(low);assert result["temporal"]["persistent_escalation"] and result["temporal"]["hysteresis_high_state"]
    assert result["decision"]=="STEP_UP_VERIFICATION"
