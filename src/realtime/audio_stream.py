"""Audio-source abstraction with file and optional microphone implementations."""
from __future__ import annotations
from abc import ABC,abstractmethod
from pathlib import Path
import time
from typing import Iterator
import numpy as np,soundfile as sf
from src.data.audio_utils import convert_to_mono,normalize_audio,resample_audio
class AudioStream(ABC):
    @abstractmethod
    def start(self)->None:...
    @abstractmethod
    def read(self)->Iterator[np.ndarray]:...
    @abstractmethod
    def stop(self)->None:...
    def __enter__(self):self.start();return self
    def __exit__(self,*args):self.stop()
class FileAudioStream(AudioStream):
    def __init__(self,path:str|Path,target_sample_rate=16000,chunk_duration_ms=200,simulate_realtime=False):self.path=Path(path);self.target_sr=target_sample_rate;self.chunk_ms=chunk_duration_ms;self.simulate=simulate_realtime;self._file=None
    def start(self)->None:self._file=sf.SoundFile(self.path)
    def read(self):
        if self._file is None:raise RuntimeError("Stream is not started")
        source_frames=max(1,round(self._file.samplerate*self.chunk_ms/1000))
        while True:
            chunk=self._file.read(source_frames,dtype="float32",always_2d=False)
            if len(chunk)==0:break
            chunk=normalize_audio(resample_audio(convert_to_mono(chunk),self._file.samplerate,self.target_sr))
            yield chunk
            if self.simulate:time.sleep(self.chunk_ms/1000)
    def stop(self)->None:
        if self._file is not None:self._file.close();self._file=None
class MicrophoneAudioStream(AudioStream):
    """Optional local microphone source; unavailable in typical Colab runtimes."""
    def __init__(self,sample_rate=16000,chunk_duration_ms=200):self.sample_rate=sample_rate;self.frames=round(sample_rate*chunk_duration_ms/1000);self._stream=None;self._running=False
    def start(self)->None:
        try:import sounddevice as sd
        except ImportError as exc:raise RuntimeError("Install optional package 'sounddevice' for microphone input") from exc
        self._stream=sd.InputStream(samplerate=self.sample_rate,channels=1,dtype="float32",blocksize=self.frames);self._stream.start();self._running=True
    def read(self):
        while self._running:
            data,_=self._stream.read(self.frames);yield data[:,0].copy()
    def stop(self)->None:
        self._running=False
        if self._stream:self._stream.stop();self._stream.close();self._stream=None
