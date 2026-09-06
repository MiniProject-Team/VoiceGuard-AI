import io, wave
import numpy as np
import pytest
from fastapi.testclient import TestClient
from api.dependencies import load_api_config
from api.main import create_app

@pytest.fixture
def config():
    value = load_api_config(); value["runtime"]["use_mock_models"] = True; return value

@pytest.fixture
def client(config):
    with TestClient(create_app(config)) as value: yield value

@pytest.fixture
def wav_audio():
    output = io.BytesIO()
    with wave.open(output, "wb") as stream:
        stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(16000); stream.writeframes((np.ones(16000, dtype="<i2") * 1000).tobytes())
    return output.getvalue()

@pytest.fixture
def active_session(client):
    sid = client.post("/api/v1/sessions", json={"speaker_id":"demo_speaker"}).json()["session_id"]
    assert client.post(f"/api/v1/sessions/{sid}/start").status_code == 200
    return sid
