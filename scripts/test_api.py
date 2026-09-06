"""Lightweight in-process Phase 7 smoke test (uses mock models)."""
from __future__ import annotations
import io, sys, wave
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import numpy as np
from fastapi.testclient import TestClient
from api.dependencies import load_api_config
from api.main import create_app

def wav_bytes():
    output = io.BytesIO()
    with wave.open(output, "wb") as stream: stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(16000); stream.writeframes((np.zeros(16000, dtype="<i2")).tobytes())
    return output.getvalue()
def main():
    config = load_api_config(); config["runtime"]["use_mock_models"] = True
    with TestClient(create_app(config)) as client:
        health = client.get("/api/v1/health").json(); created = client.post("/api/v1/sessions", json={}).json(); sid = created["session_id"]
        client.post(f"/api/v1/sessions/{sid}/start").raise_for_status(); result = client.post("/api/v1/analysis", data={"session_id":sid}, files={"audio":("sample.wav", wav_bytes(), "audio/wav")}).json(); stopped = client.post(f"/api/v1/sessions/{sid}/stop").json()
        print({"health":health["status"], "session_id":sid, "risk":result["risk"], "final":stopped["status"]})
if __name__ == "__main__": main()
