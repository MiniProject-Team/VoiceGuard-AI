from src.risk.context import evaluate_context
from src.risk.schema import RiskInput
def test_context_rules_and_unknowns(risk_config):
    value=RiskInput(call_origin="unknown",contact_match=False,transaction_amount=200000,privileged_action=True,historical_fraud_indicator=True,new_device=True,unusual_time=True,location_anomaly=True)
    score,reasons,missing=evaluate_context(value,risk_config["context"]);assert score>0 and len(reasons)==8 and not missing
def test_missing_not_safe(risk_config):
    score,reasons,missing=evaluate_context(RiskInput(),risk_config["context"]);assert score==0 and "transaction_amount" in missing and "call_origin" in missing
