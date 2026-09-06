from pathlib import Path
import yaml,pytest
@pytest.fixture
def risk_config(): return yaml.safe_load((Path(__file__).resolve().parents[2]/"configs/risk_engine.yaml").read_text())
