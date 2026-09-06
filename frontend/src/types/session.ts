import type { RiskLevel, SegmentResult } from './risk'
export type SessionStatus = 'created'|'active'|'stopping'|'completed'|'failed'
export const TERMINAL_SESSION_STATUSES: readonly SessionStatus[] = ['completed','failed']
export const isTerminalSession = (status:SessionStatus) => TERMINAL_SESSION_STATUSES.includes(status)
export interface SessionContext { call_origin?:string; contact_match?:boolean; transaction_amount?:number; transaction_type?:string; privileged_action?:boolean }
export interface CreateSessionInput { speaker_id?:string; context:SessionContext }
export interface CreatedSession { session_id:string; status:SessionStatus; created_at:string }
export interface Session { session_id:string; status:SessionStatus; speaker_id:string|null; created_at:string; started_at:string|null; completed_at:string|null; segments_processed:number; current_risk_score:number; current_risk_level:RiskLevel }
export interface SessionResults { session_id:string; results:SegmentResult[]; limit:number; offset:number; total:number }
export interface StopResult { session_id:string; status:SessionStatus; segments_processed:number; highest_risk_score:number; final_risk_level:RiskLevel }
