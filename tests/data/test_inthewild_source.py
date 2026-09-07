from src.data.phase3_export import source_group
from src.data.sources.base import SourceRecord
from src.data.sources.inthewild import InTheWildSource


def test_inthewild_label_mapping_is_explicit_and_not_inverted():
    assert InTheWildSource._classify_label("bonafide") == 0
    assert InTheWildSource._classify_label("spoof") == 1
    assert InTheWildSource._classify_label("unexpected") is None


def test_source_group_is_stable_for_resumable_sampling():
    record = SourceRecord(sample_id="record_1", original_label="spoof", voiceguard_label=1, audio={}, source_dataset="InTheWild", source_split="test", speaker_id="speaker_a")
    assert source_group(record) == source_group(record)
