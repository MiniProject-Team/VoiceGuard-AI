from fastapi import APIRouter, Depends, File, Form, UploadFile
from api.dependencies import authentication_extension_point, get_analysis_service
from api.schemas.analysis import AnalysisResponse, AnalysisSignals
from api.schemas.risk import AlertResponse, RiskResult
from api.services.analysis_service import AnalysisService, ModelUnavailable

router = APIRouter(prefix="/analysis", tags=["analysis"], dependencies=[Depends(authentication_extension_point)])

def response_for(session_id: str, result: dict) -> AnalysisResponse:
    alert = result.get("alert_event")
    return AnalysisResponse(session_id=session_id, segment_id=result["segment_id"], status="completed", analysis=AnalysisSignals(synthetic_probability=result.get("synthetic_probability"), speaker_similarity=result.get("speaker_similarity"), synthetic_detection_status=result.get("synthetic_detection_status", "unavailable"), speaker_verification_status=result.get("speaker_verification_status", "unavailable"), speaker_verified=result.get("speaker_verified")), risk=RiskResult(score=result["risk_score"], level=result["risk_level"], decision=result["decision"], recommended_action=result.get("recommended_action"), reasons=result.get("reasons", [])), alert=AlertResponse(**{key: alert[key] for key in ("severity", "alert_type", "message", "recommended_action")}) if alert else None)

@router.post("", response_model=AnalysisResponse, summary="Analyze a short WAV or FLAC segment through Phase 6")
async def analyze(session_id: str = Form(...), audio: UploadFile = File(...), service: AnalysisService | None = Depends(get_analysis_service)):
    if service is None: raise ModelUnavailable("Required analysis models are unavailable.")
    data = await audio.read(); waveform = service.decode_file(data, audio.filename); return response_for(session_id, await service.analyze(session_id, waveform))
