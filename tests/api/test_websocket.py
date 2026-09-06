import numpy as np

def create(client): return client.post("/api/v1/sessions", json={}).json()["session_id"]

def test_websocket_flow_order(client):
    sid = create(client)
    with client.websocket_connect(f"/ws/v1/sessions/{sid}") as socket:
        socket.send_json({"type":"start"}); assert socket.receive_json()["type"] == "session_started"
        socket.send_bytes((np.ones(16000, dtype="<i2") * 1000).tobytes()); assert socket.receive_json()["type"] == "analysis_result"
        socket.send_json({"type":"ping"}); assert socket.receive_json()["type"] == "pong"
        socket.send_json({"type":"stop"}); assert socket.receive_json()["type"] == "session_completed"

def test_websocket_analysis_failure_is_safe(client, monkeypatch):
    sid = create(client); client.post(f"/api/v1/sessions/{sid}/start")
    def fail(*args, **kwargs): raise RuntimeError("secret stack detail")
    monkeypatch.setattr(client.app.state.analysis.processor, "process", fail)
    with client.websocket_connect(f"/ws/v1/sessions/{sid}") as socket:
        socket.send_bytes(b"\0\0" * 100); message = socket.receive_json()
        assert message == {"type":"error", "code":"ANALYSIS_FAILED", "message":"Audio analysis could not be completed."}

def test_session_isolation(client):
    a, b = create(client), create(client); client.post(f"/api/v1/sessions/{a}/start"); client.post(f"/api/v1/sessions/{b}/start")
    with client.websocket_connect(f"/ws/v1/sessions/{a}") as socket_a, client.websocket_connect(f"/ws/v1/sessions/{b}"):
        socket_a.send_bytes(b"\0\0" * 100); assert socket_a.receive_json()["session_id"] == a
        assert client.get(f"/api/v1/sessions/{b}/results").json()["total"] == 0
