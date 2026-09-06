# Phase 9 security, privacy, and evaluation

VoiceGuard is a risk-based decision-support system. It does not guarantee deepfake detection, identity, or fraud prevention. High-impact actions should use independent verification.

## Hardened demo mode

`configs/security.yaml` sets `mode: DEMO_HARDENED_MODE`. Before a judged demonstration:

1. Keep `debug: false`, audit enabled, bounded limits, and a restricted CORS origin list.
2. Keep `configs/privacy.yaml` → `audio.retain_raw_audio: false`.
3. Set `VOICEGUARD_PSEUDONYM_KEY` to a non-public, demo-specific random value in the process environment. Do not commit it.
4. Run `python scripts/run_security_checks.py`; every actual check must report `PASS`.
5. Run `python scripts/generate_audit_report.py` and confirm `valid: true`.
6. Start the API with `python scripts/run_api.py`, then verify `/api/v1/health/ready` before opening the dashboard.

## Retention defaults

- Raw audio: processed in memory and not retained.
- Temporary uploads: held in memory by the API and discarded after the request.
- Structured risk results: retained in the in-memory session repository until deletion or process restart.
- Audit events: retained locally without audio, embeddings, context PII, filenames, or authorization data.
- Enrollment embeddings: retained only for enrolled-speaker verification. Treat them as sensitive biometric-like data.

Delete session results with `DELETE /api/v1/sessions/{id}` and an `X-Confirm-Delete: {id}` header after stopping the session. `security.privacy_delete.delete_enrolled_speaker()` safely removes the owned `.npy` and `.json` enrollment records. Shared caches are deliberately not deleted without a reliable ownership index.

Production embedding storage requires encryption at rest, strict access control, key rotation, an attributable cache index, and an audited deletion workflow.

## Audit design

Each JSONL record contains an opaque event ID, opaque session ID, timestamp, event type, risk outcome, model versions, configuration version/hash, the previous record hash, and its SHA-256 record hash. `verify_audit_chain()` detects record edits and broken links. Chained hashing is tamper evidence, not blockchain and not a substitute for remote append-only storage.

The runtime log is outside the source tree at `../voiceguard-runtime/audit.jsonl`, preventing generated audit data from being packaged with application source. The integrity report is written to `reports/phase9/audit_integrity_report.json`.

## Evaluation interpretation

Language/accent metrics are computed only from explicit metadata. Current test rows have no language values, so every Indian-language group is marked `INSUFFICIENT DATA`. Controlled telephone, noise, reverb, volume, codec-like, and speed conditions are labelled `SIMULATED CONDITION`.

The current robustness set contains only three samples. Its metrics are insufficient for generalization claims. Risk Score is a policy-oriented decision-support score, not a calibrated incident probability.

Cross-dataset, held-out-generator, replay, demographic fairness, alert-fatigue, GPU, API-delivery, and dashboard-update measurements require appropriate labeled data or hardware and remain explicitly untested where unavailable.

## Production architecture recommendations

Use TLS/HTTPS/WSS, authenticated RBAC, a secrets manager, encrypted durable stores, encrypted embedding storage, network segmentation, centralized monitoring and SIEM export, gateway rate limits, load balancing, multi-worker coordination, model/drift monitoring, an approved retention policy, and incident-response procedures. Move chained audit events to independently controlled append-only storage.
