from src.realtime.session import CallSession
def test_session_state_and_summary():
    session=CallSession("s",max_history_segments=2);session.record({"risk_score":80,"risk_level":"CRITICAL","decision":"BLOCK_OR_ESCALATE","recommended_action":"verify"});summary=session.summary(3);assert summary["segments_processed"]==1 and summary["highest_risk_score"]==80 and summary["final_risk_level"]=="CRITICAL"
