from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
import yaml
from fastapi import Request
from src.models.utils import load_yaml, resolve_path
from src.realtime.adapters import MockSpeakerVerifier, MockSyntheticDetector, SpeakerVerifierAdapter, SyntheticDetectorAdapter
from src.realtime.processor import SegmentProcessor
from src.risk.engine import RiskEngine
from api.services.analysis_service import AnalysisService
from api.services.session_service import SessionService
from api.services.websocket_manager import WebSocketManager
from security.audit import AuditLog
from security.integrity import config_hash
from security.privacy import assert_privacy_defaults,load_privacy_config
from monitoring.metrics import MetricsCollector
from mlops.model_registry import ModelRegistry

ROOT = Path(__file__).resolve().parents[1]
LOGGER = logging.getLogger(__name__)

def load_api_config(path: Path | None = None) -> dict[str, Any]:
    with (path or ROOT / "configs/api.yaml").open(encoding="utf-8") as stream: return yaml.safe_load(stream)

def initialize_services(config: dict) -> tuple[SessionService, AnalysisService | None, WebSocketManager, dict[str, str]]:
    security=load_yaml(ROOT/"configs/security.yaml");privacy=load_privacy_config(ROOT/"configs/privacy.yaml");assert_privacy_defaults(privacy);digest=config_hash([ROOT/"configs/api.yaml",ROOT/"configs/realtime.yaml",ROOT/"configs/risk_engine.yaml",ROOT/"configs/security.yaml",ROOT/"configs/privacy.yaml"]);config["config_hash"]=digest;config["model_versions"]={"phase3_model_version":"phase3-model-v1","phase4_model_version":"speechbrain-ecapa","risk_engine_version":"phase5-v1","preprocessing_version":"phase2-v1"};audit=AuditLog(ROOT/security["audit"]["path"],digest) if security["audit"]["enabled"] else None
    metrics=MetricsCollector();sessions = SessionService(max_active_sessions=int(security["limits"]["max_active_sessions"]),max_duration_seconds=int(security["limits"]["max_session_duration_seconds"]),audit=audit);sessions.monitoring=metrics; manager = WebSocketManager(int(security["limits"]["max_websocket_connections"]),int(security["rate_limits"]["websocket_connections_per_minute"]));manager.monitoring=metrics; readiness = {"phase3_synthetic_detector": "unavailable", "phase4_speaker_verifier": "unavailable", "phase5_risk_engine": "unavailable", "phase6_realtime_pipeline": "unavailable","privacy_controls":"ready","audit_log":"ready" if audit else "disabled"}
    try:
        realtime = load_yaml(ROOT / "configs/realtime.yaml"); dependencies = realtime["dependencies"]
        deployment=load_yaml(ROOT/"configs/deployment.yaml")
        if deployment["startup"].get("verify_model_hashes") and not config["runtime"].get("use_mock_models"):
            for kind in ("synthetic_detector","speaker_verifier","risk_engine"):
                registry=ModelRegistry(ROOT/f"models/registry/{kind}/registry.json");active=[item for item in registry.data["models"] if item["status"]=="ACTIVE"]
                if len(active)!=1 or not registry.validate_hash(active[0]["model_id"]):raise RuntimeError(f"No hash-valid ACTIVE {kind} is registered")
        risk = RiskEngine(load_yaml(resolve_path(dependencies["risk_config"], ROOT))); readiness["phase5_risk_engine"] = "ready"
        if config["runtime"].get("use_mock_models"):
            synthetic, speaker = MockSyntheticDetector(), MockSpeakerVerifier()
        else:
            synthetic = SyntheticDetectorAdapter(resolve_path(dependencies["phase3_model"], ROOT))
            speaker = SpeakerVerifierAdapter(resolve_path(dependencies["phase4_config"], ROOT), ROOT)
        readiness["phase3_synthetic_detector"] = "ready"; readiness["phase4_speaker_verifier"] = "ready"
        processor = SegmentProcessor(synthetic, speaker, risk); readiness["phase6_realtime_pipeline"] = "ready"
        analysis = AnalysisService(processor, sessions, config);analysis.monitoring=metrics
    except Exception:
        LOGGER.exception("event=MODEL_INITIALIZATION_FAILED")
        analysis = None
        if config["runtime"].get("fail_startup_on_model_error"): raise
    return sessions, analysis, manager, readiness

def get_config(request: Request): return request.app.state.config
def get_session_service(request: Request): return request.app.state.sessions
def get_analysis_service(request: Request): return request.app.state.analysis
def get_websocket_manager(request: Request): return request.app.state.websockets

async def authentication_extension_point(request: Request) -> None:
    """Future RBAC/authentication hook for ADMIN, SECURITY_OPERATOR, ANALYST and CLIENT_APPLICATION."""
    return None
