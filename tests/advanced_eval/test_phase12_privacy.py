from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
def test_phase12_reports_exclude_sensitive_payloads():
 text="\n".join(p.read_text(encoding="utf-8",errors="ignore") for p in (ROOT/"reports/phase12").glob("*") if p.is_file())
 assert not re.search(r"\b(?:\+91[- ]?)?[6-9]\d{9}\b",text)
 for forbidden in ('"raw_audio":', '"embeddings":', '"full_transcript":', '"secret":'):
  assert forbidden not in text
