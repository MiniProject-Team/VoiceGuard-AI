import numpy as np, pytest
from src.models.metrics import compute_metrics

def test_metrics_values_and_confusion_matrix():
    result = compute_metrics(np.array([0, 0, 1, 1]), np.array([.1, .8, .7, .9]))
    assert result["accuracy"] == .75 and result["precision"] == 2/3 and result["recall"] == 1
    assert result["f1"] == .8 and result["roc_auc"] == .75 and result["pr_auc"] == pytest.approx(5/6)
    assert result["confusion_matrix"] == [[1, 1], [0, 2]]
