from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"reports/phase13/compliance_readiness.md"
CATEGORIES={"Privacy":"implemented — consent, purpose and privacy-safe evidence metadata","Security":"partially implemented — application controls require production identity integration","Access control":"implemented — centralized logical RBAC; requires organizational identity mapping","Auditability":"implemented — governance events and integrity hashes","Data minimization":"implemented — raw audio excluded by default","Retention":"implemented — configurable expiry and hold controls","Incident response":"implemented — triage, workflow, evidence and postmortem primitives","Human oversight":"implemented — critical sensitive actions require human and independent verification","Model governance":"implemented — manual multi-check activation gate and rejection state"}
def main():
 rows="\n".join(f"| {k} | {v} |" for k,v in CATEGORIES.items());text=f"""# VoiceGuard compliance readiness mapping

This is a generic control mapping, not a legal opinion, certification, or claim of GDPR, DPDP, ISO, SOC 2, RBI, or CERT-In compliance.

| Control area | Readiness |
|---|---|
{rows}

## India-focused readiness

Production deployment may require qualified review of applicable data-protection requirements, sector-specific banking requirements, cybersecurity reporting requirements, telecom policies, contracts, and organizational policies. Applicability and sufficiency require organizational process and external review.
""";OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(text,encoding="utf-8");print(f"Compliance-readiness mapping generated: {OUT}")
if __name__=="__main__":main()
