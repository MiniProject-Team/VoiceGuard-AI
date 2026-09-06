# VoiceGuard AI Security Console

Phase 8 is a React and TypeScript security dashboard for the Phase 7 VoiceGuard API. It displays backend-issued session state, synthetic-voice probability, speaker similarity, risk decisions, timelines, and alerts. It does not calculate or simulate AI results in the browser.

## Requirements and setup

- Node.js 20 or newer
- Running Phase 7 backend and initialized Phase 3–6 dependencies

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. Public configuration:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/ws/v1
```

Values prefixed with `VITE_` are public. Never place secrets or credentials in them.

## Backend

From the repository root:

```bash
python scripts/run_api.py
```

The frontend consumes health, readiness, session create/get/start/stop, result history, multipart analysis, and `/ws/v1/sessions/{session_id}`. The configured backend CORS allowlist includes `http://localhost:5173`.

## SIH demonstration

1. Start the backend and verify `/api/v1/health/ready`.
2. Start the frontend and open **Live Analysis**.
3. Enter the claimed speaker and transaction context, then create the session.
4. Start the session; the console establishes real-time WebSocket monitoring.
5. Upload a valid mono 16 kHz WAV file. It is sent to Phase 7 and never analyzed or permanently stored by the browser.
6. Observe backend-derived probability, similarity, risk, decision, event timeline, and any alert.
7. Stop the session and inspect it on the Sessions page.

The UI labels uploaded audio as demonstration mode. It does not claim telephony connectivity or automatic transaction enforcement.

## Validation

```bash
npm test
npm run build
npm run preview
```

## Known limitations

- Phase 7 has no global session-list endpoint, so Sessions shows only sessions created during the current browser lifetime.
- Phase 7 state is in memory and is lost when the backend restarts.
- Upload mode currently uses REST analysis; WebSocket remains available for backend-pushed live events and future PCM microphone streaming.
- Microphone capture is intentionally deferred until a production-quality browser PCM16 resampling path is implemented.
- Authentication, durable audit history, notifications, and end-to-end tests remain future work.
