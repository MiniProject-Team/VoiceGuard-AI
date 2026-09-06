def test_monitoring_summary_is_aggregate(client):
 body=client.get("/api/monitoring/summary").json();assert "active_sessions" in body and "model_versions" in body;assert "raw_audio" not in body and "speaker_embedding" not in body
