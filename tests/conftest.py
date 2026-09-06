import sys
import shutil
import tempfile
from uuid import uuid4
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

@pytest.fixture(scope="session")
def voiceguard_test_root():
    root=Path(tempfile.mkdtemp(prefix="voiceguard-tests-",dir="F:/hackthon"))
    yield root
    shutil.rmtree(root,ignore_errors=True)

@pytest.fixture
def tmp_path(voiceguard_test_root):
    path=voiceguard_test_root/uuid4().hex;path.mkdir();return path
