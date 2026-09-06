"""Generate synthetic tones solely to exercise Phase 4 code, never biometrics."""
from __future__ import annotations
from pathlib import Path
import numpy as np,pandas as pd,soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
def main()->None:
    rows=[]
    for speaker,base_frequency in (("demo_speaker",180.),("demo_other",420.)):
        directory=ROOT/"data/enrollment"/speaker;directory.mkdir(parents=True,exist_ok=True)
        for index,split in enumerate(("enrollment","enrollment","validation","test"),1):
            sr=16000;time=np.arange(sr*3,dtype=np.float32)/sr
            # Harmonic mixtures make the ECAPA smoke path less degenerate than pure tones.
            audio=(.08*np.sin(2*np.pi*(base_frequency+index*3)*time)+.025*np.sin(2*np.pi*(base_frequency*2.1)*time)).astype(np.float32)
            split_dir=directory/split;split_dir.mkdir(parents=True,exist_ok=True)
            path=split_dir/f"{speaker}_{index:02d}.wav";sf.write(path,audio,sr)
            rows.append({"file_path":str(path.resolve()),"speaker_id":speaker,"split":split,"language":None,"source_dataset":"phase4_demo_tones","attack_type":"none","demo":True})
    metadata=ROOT/"data/metadata/speaker_trials.csv";metadata.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(metadata,index=False)
    print("Created DEMONSTRATION-ONLY speaker tones and disjoint enrollment/validation/test metadata.")
if __name__=="__main__":main()
