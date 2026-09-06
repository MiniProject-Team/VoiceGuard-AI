from fastapi import APIRouter,Request
from monitoring.dashboard_data import safe_monitoring_summary
router=APIRouter(prefix="/api/monitoring",tags=["monitoring"])
@router.get("/summary",summary="Privacy-safe aggregate operational metrics")
async def summary(request:Request):
 analysis=request.app.state.analysis;metrics=analysis.monitoring if analysis is not None else request.app.state.sessions.monitoring
 return safe_monitoring_summary(metrics,request.app.state.config.get("model_versions",{}))
