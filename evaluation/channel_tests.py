from __future__ import annotations
import numpy as np
from scipy.signal import butter,sosfilt,resample_poly
def add_noise(audio:np.ndarray,snr_db:float,rng:np.random.Generator|None=None)->np.ndarray:
    rng=rng or np.random.default_rng(0);power=float(np.mean(audio**2));noise_power=power/(10**(snr_db/10)) if power else 0;return np.clip(audio+rng.normal(0,np.sqrt(noise_power),len(audio)),-1,1).astype(np.float32)
def telephone_bandlimited(audio:np.ndarray,sample_rate:int=16000)->np.ndarray:
    sos=butter(6,[300,3400],btype="bandpass",fs=sample_rate,output="sos");filtered=sosfilt(sos,audio);narrow=resample_poly(filtered,1,2);return resample_poly(narrow,2,1)[:len(audio)].astype(np.float32)
def low_volume(audio:np.ndarray)->np.ndarray:return (audio*.25).astype(np.float32)
def mild_reverb(audio:np.ndarray,sample_rate:int=16000)->np.ndarray:
    impulse=np.zeros(int(.18*sample_rate)+1);impulse[0]=1;impulse[int(.06*sample_rate)]=.25;impulse[int(.14*sample_rate)]=.12;return np.clip(np.convolve(audio,impulse,mode="full")[:len(audio)],-1,1).astype(np.float32)
def codec_like(audio:np.ndarray)->np.ndarray:return (np.round(np.clip(audio,-1,1)*127)/127).astype(np.float32)
def speed_perturbation(audio:np.ndarray,factor:float=1.1)->np.ndarray:
    changed=np.interp(np.arange(0,len(audio),factor),np.arange(len(audio)),audio);return np.interp(np.linspace(0,max(0,len(changed)-1),len(audio)),np.arange(len(changed)),changed).astype(np.float32)
