from src.risk.rules import apply_rules
from src.risk.schema import RiskInput
def test_clone_and_mismatch_rules(risk_config):
    bonuses,reasons=apply_rules(RiskInput(speaker_verified=True),.9,.9,risk_config["rules"]);assert bonuses["clone_attack_bonus"]>0 and reasons
    bonuses,_=apply_rules(RiskInput(speaker_verified=False,claimed_identity=True),.1,.2,risk_config["rules"]);assert bonuses["speaker_mismatch_bonus"]>0
