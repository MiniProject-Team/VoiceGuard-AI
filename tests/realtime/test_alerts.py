from src.realtime.alerts import AlertManager
def test_alert_generation_cooldown_and_severity():
    now=[0];manager=AlertManager(True,30,"HIGH",clock=lambda:now[0]);result={"session_id":"s","segment_id":1,"risk_level":"CRITICAL","decision":"BLOCK_OR_ESCALATE","recommended_action":"verify"};first=manager.consider(result);assert first["severity"]=="critical" and manager.consider(result) is None;now[0]=31;assert manager.consider(result) is not None
