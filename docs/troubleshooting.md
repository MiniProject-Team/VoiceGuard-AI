# Troubleshooting
- Degraded: validate model/config paths and `/health/ready`.
- Offline: start `scripts/run_api.py`; verify ports and CORS.
- WebSocket failure: use REST WAV upload.
- GPU failure: use CPU; expect more latency.
- Audit failure: stop and investigate the chain.
- Unexpected risk: show actual output; never silently substitute mocks.
