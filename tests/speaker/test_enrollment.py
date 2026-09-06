import numpy as np,pytest,soundfile as sf
from src.speaker.enrollment import enroll_speaker,load_enrollment,verify_no_enrollment_test_overlap
def test_multiple_references_and_storage(tmp_path):
    files=[]
    for index in range(2):
        path=tmp_path/f"{index}.wav";sf.write(path,np.ones(1600)*.1,16000);files.append(path)
    metadata=enroll_speaker("alice",files,lambda p:np.array([1.,int(p.stem)+1]),tmp_path/"emb",{"model_name":"mock"},2)
    vector,loaded=load_enrollment("alice",tmp_path/"emb");assert metadata["number_of_reference_files"]==2 and vector.shape==(2,) and loaded["embedding_dimension"]==2
    with pytest.raises(ValueError,match="leakage"):verify_no_enrollment_test_overlap(loaded,files[0])
def test_missing_and_insufficient(tmp_path):
    with pytest.raises(ValueError):enroll_speaker("x",[],lambda p:np.ones(2),tmp_path,{},2)
    with pytest.raises(FileNotFoundError):enroll_speaker("x",[tmp_path/"a",tmp_path/"b"],lambda p:np.ones(2),tmp_path,{},2)
