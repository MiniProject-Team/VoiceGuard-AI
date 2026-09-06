import pandas as pd
from src.data.metadata import PROCESSED_COLUMNS, ensure_processed_schema, find_duplicates

def test_required_columns_and_labels():
    frame = ensure_processed_schema(pd.DataFrame([{"segment_id": "a", "label": 0, "label_name": "real"}]))
    assert list(frame.columns) == PROCESSED_COLUMNS
    assert frame.loc[0, "label"] == 0 and frame.loc[0, "label_name"] == "real"

def test_duplicates():
    frame = pd.DataFrame({"source_file_hash": ["x", "x", "y"]})
    assert len(find_duplicates(frame)) == 2
