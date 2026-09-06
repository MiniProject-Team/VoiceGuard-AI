import numpy as np
from evaluation.channel_tests import add_noise,codec_like,low_volume,mild_reverb,telephone_bandlimited,speed_perturbation
from evaluation.latency_tests import real_time_factor,summarize
def test_controlled_channel_transforms_preserve_shape():
 audio=np.sin(np.linspace(0,20,16000)).astype(np.float32)
 for transformed in [add_noise(audio,10),codec_like(audio),low_volume(audio),mild_reverb(audio),telephone_bandlimited(audio),speed_perturbation(audio)]:assert transformed.shape==audio.shape and np.isfinite(transformed).all()
 assert real_time_factor(.5,1)==.5 and summarize([1,2,3])["p95"]>=2
