from src.realtime.aggregator import ResultAggregator
def test_bounded_history_and_risk_state():
    agg=ResultAggregator(2);agg.add({"risk_score":70,"risk_level":"HIGH"});state=agg.add({"risk_score":80,"risk_level":"CRITICAL"});agg.add({"risk_score":10,"risk_level":"LOW"});assert len(agg.results)==2 and state["maximum_risk"]==80 and state["consecutive_high_count"]==2
