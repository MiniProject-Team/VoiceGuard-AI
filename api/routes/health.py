from fastapi import APIRouter, Request, Response
from api.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=HealthResponse, summary="Service health")
async def health(): return HealthResponse(status="healthy")

@router.get("/live", response_model=HealthResponse, summary="Process liveness")
async def live(): return HealthResponse(status="alive")

@router.get("/ready", response_model=HealthResponse, summary="Model and pipeline readiness")
async def ready(request: Request, response: Response):
    components = request.app.state.readiness; is_ready = all(value == "ready" for value in components.values())
    if not is_ready: response.status_code = 503
    return HealthResponse(status="ready" if is_ready else "degraded", components=components)
