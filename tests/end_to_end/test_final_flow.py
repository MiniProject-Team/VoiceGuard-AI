import numpy as np
from fastapi.testclient import TestClient
from api.dependencies import load_api_config
from api.main import create_app
from integrations.local_enterprise import simulate_enterprise_action
def test_api_websocket_dashboard_event_and_enterprise_simulation():
 config=load_api_config();config["runtime"]["use_mock_models"]=True
 with TestClient(create_app(config)) as client:
  sid=client.post("/api/v1/sessions",json={"context":{"transaction_amount":1000000,"privileged_action":True,"call_origin":"unknown"}}).json()["session_id"]
  with client.websocket_connect(f"/ws/v1/sessions/{sid}") as socket:
   socket.send_json({"type":"start"});assert socket.receive_json()["type"]=="session_started";socket.send_bytes((np.ones(16000,dtype="<i2")*1000).tobytes());event=socket.receive_json();assert event["type"]=="analysis_result";assert event["session_id"]==sid
   action=simulate_enterprise_action(event["decision"]);assert action.mode=="SIMULATION MODE" and action.source_decision==event["decision"]
def test_critical_enterprise_fallback_holds_for_review():
 action=simulate_enterprise_action("BLOCK_OR_ESCALATE");assert action.status=="HOLD FOR REVIEW" and "MFA" in action.required_controls
