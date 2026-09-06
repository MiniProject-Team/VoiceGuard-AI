from fastapi import APIRouter, Depends, Query,Header,HTTPException
from api.dependencies import authentication_extension_point, get_session_service
from api.schemas.common import MessageResponse
from api.schemas.risk import SegmentResult
from api.schemas.session import CreateSessionRequest, CreateSessionResponse, SessionResponse, SessionResultsResponse, StopSessionResponse
from api.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"], dependencies=[Depends(authentication_extension_point)])

def representation(item):
    return SessionResponse(session_id=item.session_id, status=item.status, speaker_id=item.speaker_id, created_at=item.created_at, started_at=item.started_at, completed_at=item.completed_at, segments_processed=len(item.results), current_risk_score=item.current_risk_score, current_risk_level=item.current_risk_level)

@router.post("", status_code=201, response_model=CreateSessionResponse, summary="Create an isolated analysis session")
async def create_session(body: CreateSessionRequest, service: SessionService = Depends(get_session_service)):
    item = await service.create(body.speaker_id, body.context.model_dump(exclude_none=True)); return CreateSessionResponse(session_id=item.session_id, status=item.status, created_at=item.created_at)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, service: SessionService = Depends(get_session_service)): return representation(await service.get(session_id))

@router.post("/{session_id}/start", response_model=MessageResponse)
async def start_session(session_id: str, service: SessionService = Depends(get_session_service)):
    item = await service.start(session_id); return MessageResponse(session_id=item.session_id, status=item.status)

@router.post("/{session_id}/stop", response_model=StopSessionResponse)
async def stop_session(session_id: str, service: SessionService = Depends(get_session_service)):
    item = await service.stop(session_id); return StopSessionResponse(session_id=item.session_id, status=item.status, segments_processed=len(item.results), highest_risk_score=item.highest_risk_score, final_risk_level=item.current_risk_level)

@router.get("/{session_id}/results", response_model=SessionResultsResponse)
async def results(session_id: str, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), service: SessionService = Depends(get_session_service)):
    item, rows = await service.results(session_id, limit, offset); clean = [SegmentResult(**{key: row.get(key) for key in SegmentResult.model_fields}) for row in rows]
    return SessionResultsResponse(session_id=session_id, results=clean, limit=limit, offset=offset, total=len(item.results))

@router.delete("/{session_id}",status_code=204,summary="Delete retained session results")
async def delete_session(session_id:str,x_confirm_delete:str|None=Header(default=None),service:SessionService=Depends(get_session_service)):
    if x_confirm_delete!=session_id:raise HTTPException(status_code=400,detail="X-Confirm-Delete must match the session identifier.")
    await service.delete(session_id)
