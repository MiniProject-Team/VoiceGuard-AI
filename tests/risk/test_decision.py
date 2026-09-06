from src.risk.decision import decision_for,risk_level
def test_level_decisions(risk_config):
    expected=[(0,"LOW","ALLOW"),(30,"MEDIUM","MONITOR"),(60,"HIGH","STEP_UP_VERIFICATION"),(80,"CRITICAL","BLOCK_OR_ESCALATE")]
    for score,level,decision in expected:
        assert risk_level(score,risk_config["risk"]["thresholds"])==level and decision_for(level,risk_config["decisions"])[0]==decision
