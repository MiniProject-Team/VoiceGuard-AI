def test_valid_analysis_and_history(client, active_session, wav_audio):
    response = client.post("/api/v1/analysis", data={"session_id":active_session}, files={"audio":("voice.wav",wav_audio,"audio/wav")})
    assert response.status_code == 200; body = response.json(); assert body["risk"]["score"] >= 0
    history = client.get(f"/api/v1/sessions/{active_session}/results").json(); assert history["total"] == 1

def test_audio_rejections(client, active_session):
    empty = client.post("/api/v1/analysis", data={"session_id":active_session}, files={"audio":("voice.wav",b"","audio/wav")})
    assert empty.status_code == 400 and empty.json()["error"]["code"] == "INVALID_AUDIO"
    invalid = client.post("/api/v1/analysis", data={"session_id":active_session}, files={"audio":("voice.exe",b"bad","application/octet-stream")})
    assert invalid.status_code == 400 and invalid.json()["error"]["code"] == "UNSUPPORTED_AUDIO_FORMAT"
    try: client.app.state.analysis.decode_file(b"x" * (5 * 1024 * 1024 + 1), "large.wav")
    except Exception as exc: assert exc.code == "AUDIO_TOO_LARGE"
    else: assert False

def test_missing_session(client, wav_audio):
    response = client.post("/api/v1/analysis", data={"session_id":"missing"}, files={"audio":("voice.wav",wav_audio,"audio/wav")})
    assert response.status_code == 404
