import numpy as np
from security.privacy_delete import delete_enrolled_speaker
def test_delete_speaker_removes_only_owned_files(tmp_path):
 np.save(tmp_path/"speaker.npy",np.ones(2));(tmp_path/"speaker.json").write_text("{}");(tmp_path/"other.json").write_text("{}");removed=delete_enrolled_speaker("speaker",tmp_path);assert sorted(removed)==["speaker.json","speaker.npy"] and (tmp_path/"other.json").exists()
