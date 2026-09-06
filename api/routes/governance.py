from fastapi import APIRouter,Header,HTTPException,Request
from pydantic import BaseModel
from governance.roles import Permission,authorize
from responsible_ai.decision_record import HumanAction
from incident_response.triage import triage
from incident_response.workflow import transition
router=APIRouter(tags=["governance"])
def role(x_role:str|None):
 if not x_role:raise HTTPException(401,"Authenticated role required.")
 return x_role
def allowed(r,p):
 try:authorize(r,p)
 except (PermissionError,ValueError) as e:raise HTTPException(403,str(e))
class ReviewDecision(BaseModel):action:HumanAction;reason:str|None=None;note:str|None=None
class TriageRequest(BaseModel):financial_impact:float=0;privileged_action:bool=False;confirmed_loss:bool=False;system_compromise:bool=False
class ResolveRequest(BaseModel):resolution:str;close:bool=False
@router.get("/api/governance/policies")
def policies(request:Request,x_role:str|None=Header(None)):
 allowed(role(x_role),Permission.POLICY_READ);return request.app.state.policy_store.list()
@router.get("/api/reviews")
def reviews(request:Request,x_role:str|None=Header(None)):
 allowed(role(x_role),Permission.SESSION_REVIEW);return request.app.state.review_queue.list()
@router.post("/api/reviews/{decision_id}/decision")
def review(decision_id:str,body:ReviewDecision,request:Request,x_role:str|None=Header(None)):
 try:return request.app.state.review_queue.decide(decision_id,body.action,role(x_role),body.reason,body.note,request.app.state.governance_log).to_dict()
 except (KeyError,ValueError,PermissionError) as e:raise HTTPException(400,str(e))
@router.get("/api/incidents")
def incidents(request:Request,x_role:str|None=Header(None)):
 allowed(role(x_role),Permission.INCIDENT_READ);return request.app.state.incident_store.list()
@router.get("/api/incidents/{incident_id}")
def incident(incident_id:str,request:Request,x_role:str|None=Header(None)):
 allowed(role(x_role),Permission.INCIDENT_READ)
 try:return request.app.state.incident_store.get(incident_id).to_dict()
 except KeyError:raise HTTPException(404,"Incident not found.")
@router.post("/api/incidents/{incident_id}/triage")
def triage_endpoint(incident_id:str,body:TriageRequest,request:Request,x_role:str|None=Header(None)):
 try:return triage(request.app.state.incident_store.get(incident_id),role(x_role),**body.model_dump()).to_dict()
 except KeyError:raise HTTPException(404,"Incident not found.")
@router.post("/api/incidents/{incident_id}/resolve")
def resolve(incident_id:str,body:ResolveRequest,request:Request,x_role:str|None=Header(None)):
 try:
  item=request.app.state.incident_store.get(incident_id);transition(item,"RESOLVED",role(x_role),body.resolution)
  if body.close:transition(item,"CLOSED",role(x_role),audit=request.app.state.governance_log)
  return item.to_dict()
 except KeyError:raise HTTPException(404,"Incident not found.")
 except (ValueError,PermissionError) as e:raise HTTPException(400,str(e))
