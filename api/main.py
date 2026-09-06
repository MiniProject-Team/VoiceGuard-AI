from __future__ import annotations
import json, logging, time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.dependencies import initialize_services, load_api_config
from api.routes import analysis, health, sessions, websocket, monitoring, governance
from governance.governance_log import GovernanceLog
from governance.policy import PolicyStore
from responsible_ai.review_queue import ReviewQueue
from incident_response.incident import IncidentStore
from api.services.analysis_service import AudioError, ModelUnavailable
from api.services.session_service import InvalidSessionState, SessionNotFound

VERSION = "1.0.0"
LOGGER = logging.getLogger("voiceguard.api")

def error_response(code: str, message: str, request_id: str | None, status: int):
    return JSONResponse(status_code=status, content={"error":{"code":code, "message":message, "request_id":request_id}})

def create_app(config: dict | None = None) -> FastAPI:
    settings = config or load_api_config()
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        logging.basicConfig(level=getattr(logging, settings["logging"]["level"].upper(), logging.INFO), format="%(levelname)s %(message)s")
        application.state.config = settings
        application.state.sessions, application.state.analysis, application.state.websockets, application.state.readiness = initialize_services(settings)
        application.state.started_at = time.time()
        application.state.governance_log=GovernanceLog()
        application.state.policy_store=PolicyStore(application.state.governance_log)
        application.state.review_queue=ReviewQueue()
        application.state.incident_store=IncidentStore()
        if not settings["security"].get("authentication_enabled"):
            LOGGER.warning("VoiceGuard API running in DEVELOPMENT/DEMONSTRATION mode. Authentication is disabled. Do not expose this service directly to the public internet.")
        yield
        application.state.analysis = None
    application = FastAPI(title="VoiceGuard AI Security API", description="Versioned REST and WebSocket interface for real-time voice impersonation risk analysis. Create and start a session before submitting audio. WebSocket audio is raw PCM16, 16 kHz, mono, little-endian.", version=VERSION, lifespan=lifespan,debug=bool(settings["security"].get("debug",False)))
    application.state.config = settings; application.state.rate_windows = defaultdict(deque)
    if settings["security"].get("cors_enabled"):
        application.add_middleware(CORSMiddleware, allow_origins=settings["security"]["allowed_origins"], allow_credentials=True, allow_methods=["GET","POST"], allow_headers=["Content-Type","X-Request-ID"])
    @application.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid4().hex; request.state.request_id = request_id; started = time.perf_counter()
        limit = None
        if request.method == "POST" and request.url.path == "/api/v1/sessions": limit = int(settings["security"]["session_creation_per_minute"])
        elif request.method == "POST" and request.url.path == "/api/v1/analysis": limit = int(settings["security"]["analysis_per_minute"])
        if limit:
            key = (request.client.host if request.client else "unknown", request.url.path); window = application.state.rate_windows[key]; now = time.monotonic()
            while window and now - window[0] >= 60: window.popleft()
            if len(window) >= limit: return error_response("RATE_LIMITED", "Request rate limit exceeded.", request_id, 429)
            window.append(now)
        try: response = await call_next(request)
        except Exception:
            LOGGER.exception("request_id=%s endpoint=%s event=INTERNAL_ERROR", request_id, request.url.path); response = error_response("INTERNAL_ERROR", "An internal error occurred.", request_id, 500)
        response.headers["X-Request-ID"] = request_id
        LOGGER.info("request_id=%s endpoint=%s status=%s processing_time=%.4f", request_id, request.url.path, response.status_code, time.perf_counter()-started)
        return response
    @application.exception_handler(SessionNotFound)
    async def missing(request, exc): return error_response("SESSION_NOT_FOUND", "Session was not found.", request.state.request_id, 404)
    @application.exception_handler(InvalidSessionState)
    async def state(request, exc): return error_response("INVALID_SESSION_STATE", str(exc), request.state.request_id, 409)
    @application.exception_handler(AudioError)
    async def audio_error(request, exc):
        statuses = {"AUDIO_TOO_LARGE":413, "AUDIO_TOO_LONG":413, "SERVER_BUSY":429}; return error_response(exc.code, str(exc), request.state.request_id, statuses.get(exc.code, 400))
    @application.exception_handler(ModelUnavailable)
    async def unavailable(request, exc): return error_response("MODEL_UNAVAILABLE", str(exc), request.state.request_id, 503)
    @application.exception_handler(RequestValidationError)
    async def validation(request, exc): return error_response("VALIDATION_ERROR", "Request validation failed.", request.state.request_id, 422)
    application.include_router(health.router, prefix="/api/v1"); application.include_router(sessions.router, prefix="/api/v1"); application.include_router(analysis.router, prefix="/api/v1"); application.include_router(websocket.router)
    application.include_router(monitoring.router)
    application.include_router(governance.router)
    return application

app = create_app()
