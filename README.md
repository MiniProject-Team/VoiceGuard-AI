# VoiceGuard AI

**SIH26104 — AI-Powered Near-Real-Time Detection and Prevention Support for Voice-Cloning Impersonation Attacks**

VoiceGuard is a near-real-time voice security layer that combines synthetic-speech detection, speaker verification, contextual risk scoring, and step-up verification to reduce voice-cloning impersonation risk in sensitive workflows.

## Problem and solution
Voice cloning can impersonate CXOs, officials, bank customers, and trusted individuals to solicit fund transfers, approvals, credentials, or confidential data. A normal detector returns `REAL / FAKE`; VoiceGuard combines synthetic likelihood, speaker consistency, context, an explainable decision-support score, alerts, and a recommended action.

## Architecture and features
Audio passes through preprocessing, buffer/VAD, a Wav2Vec2 detector, SpeechBrain ECAPA-TDNN verification, contextual risk policy, FastAPI/WebSocket delivery, and a React dashboard. A local enterprise fallback is explicitly `SIMULATION MODE`. Raw audio is not retained.

Technology: Python, NumPy, SciPy, pandas, PyTorch, Transformers/Wav2Vec2, SpeechBrain/ECAPA-TDNN, FastAPI, Pydantic, WebSocket, React, TypeScript, Vite, Tailwind CSS, Recharts, and Lucide React.

## Install, train, and run
```powershell
python -m pip install -r requirements.txt
cd frontend; npm install; cd ..
python scripts/validate_project.py
python scripts/start_sih_demo.py
```
In a second terminal run `cd frontend; npm run dev`, then open `http://localhost:5173`. API docs are at `http://127.0.0.1:8000/docs`. Dataset/training utilities are under `scripts/` and `src/data/`.

## Evaluation
Current Phase 3 metrics use only three segments: accuracy 0.3333, F1 0, ROC-AUC 1.0, FNR 1.0. Phase 4's small demo evaluation reports EER 0 at threshold 0.825. Neither supports a generalization claim. Language metadata is absent and reported as `INSUFFICIENT DATA`.

## Privacy, security, and limitations
Hardened mode disables raw-audio retention/debug, restricts CORS, validates input, bounds resources, rate-limits interfaces, redacts logs, and chains audit records. Embeddings require encrypted production storage. Actual four-scenario validation returned MEDIUM, MEDIUM, MEDIUM, and HIGH rather than conceptual LOW, HIGH, HIGH/CRITICAL, and CRITICAL; this is an experimental SIH prototype, not production ready. Speaker verification is not identity proof and sensitive actions require independent authentication.

Future work: larger Indian-language/cross-generator datasets, anti-replay and adversarial robustness, telecom adapters, edge acceleration, drift monitoring, production RBAC, encrypted storage, and SIEM integration.

Suggested team ownership: ML/data, speaker verification, risk/security, backend/integration, frontend/demo, and evaluation/documentation. Replace with actual team details.
