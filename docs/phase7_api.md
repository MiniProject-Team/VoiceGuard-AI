# Phase 7 — API and WebSocket backend

VoiceGuard exposes one shared Phase 6 analysis service to REST and WebSocket clients. Phase 6 calls the existing synthetic detector (Phase 3), speaker verifier (Phase 4), and risk engine (Phase 5). Models are initialized once during application lifespan; inference is serialized and admission is bounded.

## Run and inspect

```bash
pip install -r requirements.txt
python scripts/run_api.py
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/sessions -H "Content-Type: application/json" -d "{}"
curl http://localhost:8000/api/v1/sessions/SESSION_ID
```

Swagger UI is at `http://localhost:8000/docs`, ReDoc at `/redoc`, and the schema at `/openapi.json`.

## REST contract

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | API health |
| GET | `/api/v1/health/live` | Process liveness only |
| GET | `/api/v1/health/ready` | Phase 3–6 readiness; returns 503 when degraded |
| POST | `/api/v1/sessions` | Create a session |
| GET | `/api/v1/sessions/{id}` | Session status/current risk |
| POST | `/api/v1/sessions/{id}/start` | Transition CREATED → ACTIVE |
| POST | `/api/v1/sessions/{id}/stop` | Transition ACTIVE → STOPPING → COMPLETED |
| GET | `/api/v1/sessions/{id}/results?limit=50&offset=0` | Paginated structured history (maximum 100) |
| POST | `/api/v1/analysis` | Multipart fields `session_id` and `audio` |

REST accepts mono, 16 kHz WAV or FLAC up to 5 MiB and 10 seconds. Empty, corrupt, stereo, wrong-rate, unsupported, and oversized input is rejected. The response contains probabilities, risk, decision, recommended action, and an optional deduplicated alert; never audio or embeddings.

## WebSocket protocol

Connect to `/ws/v1/sessions/{session_id}` after creating a session. Send `{"type":"start"}`, then binary audio frames. A binary frame is headerless signed PCM, little-endian, 16-bit, mono, 16 kHz. Do not send a WAV header. Each frame is limited to 1 MiB and 10 seconds.

Server messages are `session_started`, `analysis_result`, `alert`, `session_completed`, `error`, and `pong`. Client control messages are `start`, `stop`, and `ping`; audio is binary.

```text
connect → {"type":"start"} → session_started
binary PCM16 frame → analysis_result → optional alert
{"type":"ping"} → pong
{"type":"stop"} → session_completed
```

Results are broadcast only to sockets attached to the same session, allowing a dashboard and security console to observe one call without cross-session leakage.

## Security and deployment

Inputs are strictly validated; client-supplied risk or decision fields are not accepted. Session IDs use random UUID4 values. Request IDs, bounded inference admission, connection caps, simple per-process rate limits, explicit CORS origins, generic errors, and privacy-safe logs are enabled. Authentication is intentionally disabled in the prototype and startup prints a development warning. The dependency hook is the extension point for future ADMIN, SECURITY_OPERATOR, ANALYST, and CLIENT_APPLICATION authorization.

Production requires authentication, TLS, an API gateway, distributed rate limiting, durable storage, multi-worker connection coordination, monitoring, and a model-serving concurrency strategy. In-memory sessions, metrics, connection state, and alert cooldowns do not survive restart and are not shared across workers.

## SIH demo

Start the API, open `/docs`, create and start a session, connect its WebSocket, and send PCM frames. Phase 6 obtains Phase 3 probability and Phase 4 similarity, then Phase 5 calculates server-owned risk and decision. Observe results and alerts, stop the session, and retrieve its history. Phase 8 should consume the REST schemas and this WebSocket message contract; it must never access models directly or submit trusted risk values.
