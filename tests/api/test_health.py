def test_health_live_and_ready(client):
    assert client.get("/api/v1/health").json()["status"] == "healthy"
    assert client.get("/api/v1/health/live").json()["status"] == "alive"
    ready = client.get("/api/v1/health/ready")
    assert ready.status_code == 200
    assert ready.json()["components"]["phase6_realtime_pipeline"] == "ready"

def test_no_unversioned_health(client): assert client.get("/health").status_code == 404
