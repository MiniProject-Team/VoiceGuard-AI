import json
import numpy as np,soundfile as sf
from src.speaker.verifier import SpeakerVerifier
def _enroll(directory):
    directory.mkdir();np.save(directory/"alice.npy",np.array([1.,0.],dtype=np.float32));(directory/"alice.json").write_text(json.dumps({"reference_files":[]}))
def _config():return {"sample_rate":16000,"minimum_duration_seconds":1.5,"max_duration_seconds":10.,"window_duration_seconds":5.,"window_hop_seconds":2.5,"maximum_silence_fraction":.95,"clipping_fraction_limit":.05}
def test_valid_missing_and_threshold(tmp_path):
    store=tmp_path/"emb";_enroll(store);audio=tmp_path/"test.wav";sf.write(audio,np.sin(np.arange(32000)*.1)*.1,16000)
    verifier=SpeakerVerifier(store,lambda waveform,sr:np.array([1.,0.]),_config(),.7)
    assert verifier.verify("alice",audio)["verified"] is True
    assert verifier.verify("missing",audio)["status"]=="speaker_not_enrolled"
def test_insufficient_and_uncalibrated(tmp_path):
    store=tmp_path/"emb";_enroll(store);short=tmp_path/"short.wav";sf.write(short,np.ones(1000)*.1,16000)
    verifier=SpeakerVerifier(store,lambda waveform,sr:np.array([1.,0.]),_config(),None)
    assert verifier.verify("alice",short)["status"]=="insufficient_audio"
    long=tmp_path/"long.wav";sf.write(long,np.sin(np.arange(32000)*.1)*.1,16000)
    assert verifier.verify("alice",long)["status"]=="threshold_not_calibrated"
