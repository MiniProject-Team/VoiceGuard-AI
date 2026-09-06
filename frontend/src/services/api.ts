import type { AnalysisResponse, ApiErrorEnvelope, HealthResponse, MonitoringSummary } from '../types/api'
import type { CreateSessionInput, CreatedSession, Session, SessionResults, StopResult } from '../types/session'
import { API_BASE_URL, API_ORIGIN_URL } from '../utils/constants'

export class ApiError extends Error { constructor(public code:string,message:string,public status:number){super(message)} }
async function request<T>(path:string,options?:RequestInit,baseUrl=API_BASE_URL):Promise<T>{
  let response:Response
  try{response=await fetch(`${baseUrl}${path}`,{...options,headers:{Accept:'application/json',...options?.headers}})}catch{throw new ApiError('BACKEND_OFFLINE','Unable to connect to VoiceGuard backend.',0)}
  if(!response.ok){let payload:ApiErrorEnvelope|undefined;try{payload=await response.json() as ApiErrorEnvelope}catch{payload=undefined}throw new ApiError(payload?.error.code??'REQUEST_FAILED',payload?.error.message??'VoiceGuard request failed.',response.status)}
  return response.json() as Promise<T>
}
export const healthCheck=()=>request<HealthResponse>('/health')
export const livenessCheck=()=>request<HealthResponse>('/health/live')
export async function readinessCheck():Promise<HealthResponse>{try{return await request<HealthResponse>('/health/ready')}catch(error){if(error instanceof ApiError&&error.status===503){const response=await fetch(`${API_BASE_URL}/health/ready`);return response.json() as Promise<HealthResponse>}throw error}}
export const monitoringSummary=()=>request<MonitoringSummary>('/api/monitoring/summary',undefined,API_ORIGIN_URL)
export const createSession=(body:CreateSessionInput)=>request<CreatedSession>('/sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
export const getSession=(id:string)=>request<Session>(`/sessions/${encodeURIComponent(id)}`)
export const startSession=(id:string)=>request<{session_id:string;status:string}>(`/sessions/${encodeURIComponent(id)}/start`,{method:'POST'})
export const stopSession=(id:string)=>request<StopResult>(`/sessions/${encodeURIComponent(id)}/stop`,{method:'POST'})
export const getSessionResults=(id:string,limit=100,offset=0)=>request<SessionResults>(`/sessions/${encodeURIComponent(id)}/results?limit=${limit}&offset=${offset}`)
export const analyzeAudio=(id:string,file:File)=>{const body=new FormData();body.set('session_id',id);body.set('audio',file);return request<AnalysisResponse>('/analysis',{method:'POST',body})}
