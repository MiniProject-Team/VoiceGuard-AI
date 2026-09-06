# Judge Q&A
1. **Why not speaker verification alone?** Clones may preserve speaker traits; multiple independent signals reduce single-model dependence.
2. **Why Wav2Vec2?** It provides learned speech representations and integrates with the existing fine-tuned classifier.
3. **Real time?** Bounded PCM chunks pass through a serialized near-real-time pipeline and WebSocket results.
4. **New clone model?** Measure drift, collect consented examples, evaluate held-out generators, and retrain/version models.
5. **Privacy?** In-memory audio, minimal results, no API embeddings, redaction, deletion, and auditable policy.
6. **Why not recordings?** Minimization reduces breach impact; retention requires explicit governance.
7. **Model wrong?** Treat output as decision support and use independent verification.
8. **False alarms?** Calibrate thresholds on representative data, temporal smoothing, cooldown, and human review.
9. **Indian languages?** The pipeline is language-agnostic, but performance must be measured on labeled language data; current results are insufficient.
10. **Bank integration?** REST/WebSocket plus policy events; current bank adapter is local simulation only.
11. **Phone networks?** Not directly; SIP/carrier integration needs platform cooperation.
12. **Difference?** It returns synthetic, speaker, context, risk, explanation, and action—not only real/fake.
13. **Can it be bypassed?** Potentially; no detector is unbreakable, so layered authentication remains essential.
14. **Evaluation?** Held-out metrics, speaker trials, robustness transformations, calibration, errors, latency, and audit checks.
15. **Scalability?** Prototype inference is serialized; production needs model serving, queues, load balancing, and shared state.
