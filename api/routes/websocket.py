from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.routes.analysis import response_for
from api.services.analysis_service import AudioError
from api.services.session_service import InvalidSessionState, SessionNotFound
from api.services.websocket_manager import ConnectionLimitError

router = APIRouter(tags=["websocket"])

def now(): return datetime.now(timezone.utc).isoformat()

@router.websocket("/ws/v1/sessions/{session_id}")
async def session_socket(websocket: WebSocket, session_id: str):
    app = websocket.app; sessions, analysis, manager = app.state.sessions, app.state.analysis, app.state.websockets
    try: await sessions.get(session_id)
    except SessionNotFound: await websocket.close(code=4404, reason="Session not found"); return
    try: await manager.connect(session_id, websocket)
    except ConnectionLimitError: await websocket.close(code=4429, reason="Connection limit reached"); return
    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect": break
            if message.get("bytes") is not None:
                if analysis is None: await websocket.send_json({"type":"error", "code":"MODEL_UNAVAILABLE", "message":"Required analysis models are unavailable."}); continue
                try:
                    result = await analysis.analyze(session_id, analysis.decode_pcm(message["bytes"])); payload = response_for(session_id, result).model_dump(mode="json")
                    wire = {"type":"analysis_result", "session_id":session_id, "segment_id":payload["segment_id"], **payload["analysis"], "risk_score":payload["risk"]["score"], "risk_level":payload["risk"]["level"], "decision":payload["risk"]["decision"], "recommended_action":payload["risk"].get("recommended_action"), "reasons":payload["risk"].get("reasons", [])}
                    await manager.send_to_session(session_id, wire)
                    if payload["alert"]: await manager.send_to_session(session_id, {"type":"alert", "session_id":session_id, **payload["alert"]})
                except AudioError as exc: await websocket.send_json({"type":"error", "code":exc.code, "message":str(exc)})
                except InvalidSessionState as exc: await websocket.send_json({"type":"error", "code":"INVALID_SESSION_STATE", "message":str(exc)})
                except Exception: await websocket.send_json({"type":"error", "code":"ANALYSIS_FAILED", "message":"Audio analysis could not be completed."})
                continue
            try: body = __import__("json").loads(message.get("text") or "{}")
            except Exception: await websocket.send_json({"type":"error", "code":"WEBSOCKET_ERROR", "message":"Invalid JSON message."}); continue
            kind = body.get("type")
            try:
                if kind == "start": await sessions.start(session_id); await manager.send_to_session(session_id, {"type":"session_started", "session_id":session_id, "timestamp":now()})
                elif kind == "stop":
                    item = await sessions.stop(session_id); await manager.send_to_session(session_id, {"type":"session_completed", "session_id":session_id, "segments_processed":len(item.results), "highest_risk_score":item.highest_risk_score, "final_risk_level":item.current_risk_level, "timestamp":now()})
                elif kind == "ping": await websocket.send_json({"type":"pong", "timestamp":now()})
                else: await websocket.send_json({"type":"error", "code":"WEBSOCKET_ERROR", "message":"Message type must be start, stop, or ping; send audio as a binary frame."})
            except InvalidSessionState as exc: await websocket.send_json({"type":"error", "code":"INVALID_SESSION_STATE", "message":str(exc)})
    except WebSocketDisconnect: pass
    finally: await manager.disconnect(session_id, websocket)
