def test_lifecycle_and_history(client):
    created = client.post("/api/v1/sessions", json={"speaker_id":"CEO_001", "context":{"privileged_action":True}})
    assert created.status_code == 201; sid = created.json()["session_id"]; assert sid.startswith("SESSION_") and len(sid) == 40
    assert client.get(f"/api/v1/sessions/{sid}").json()["status"] == "created"
    assert client.post(f"/api/v1/sessions/{sid}/start").json()["status"] == "active"
    assert client.get(f"/api/v1/sessions/{sid}/results?limit=1").json()["results"] == []
    assert client.post(f"/api/v1/sessions/{sid}/stop").json()["status"] == "completed"

def test_missing_and_invalid_transition(client, active_session):
    error = client.get("/api/v1/sessions/not-real")
    assert error.status_code == 404 and error.json()["error"]["code"] == "SESSION_NOT_FOUND"
    conflict = client.post(f"/api/v1/sessions/{active_session}/start")
    assert conflict.status_code == 409 and conflict.json()["error"]["code"] == "INVALID_SESSION_STATE"

def test_strict_client_input(client):
    response = client.post("/api/v1/sessions", json={"risk_score":0, "risk_level":"LOW"})
    assert response.status_code == 422
