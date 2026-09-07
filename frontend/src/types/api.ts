import type { RiskResult, SecurityAlert } from './risk'
export interface HealthResponse { status:string; service:string; version:string; components?:Record<string,string>|null }
export interface MonitoringSummary { metrics:{active_sessions:number;sessions_completed:number;segments_processed:number;latency:{average_ms:number;p95_ms:number};average_rtf:number;score_distributions:Record<string,{count:number;mean:number|null;min:number|null;max:number|null}>;risk_distribution:Record<string,number>;alerts_triggered:number;errors:Record<string,number>;error_rate:number;degraded_mode_events:number};operational_alerts:Array<{code:string;severity:string;message:string}>;model_versions:Record<string,string> }
export interface AnalysisResponse { session_id:string; segment_id:number; status:'completed'; analysis:{synthetic_probability:number|null;synthetic_detection_status:string;speaker_similarity:number|null;speaker_verification_status:string;speaker_verified:boolean|null}; risk:RiskResult; alert:SecurityAlert|null }
export interface ApiErrorEnvelope { error:{code:string;message:string;request_id?:string|null} }
export type WsState = 'disconnected'|'connecting'|'connected'|'reconnecting'|'failed'
export type ServerMessage =
 | {type:'session_started';session_id:string;timestamp:string}
 | {type:'analysis_result';session_id:string;segment_id:number;synthetic_probability:number|null;synthetic_detection_status:string;speaker_similarity:number|null;speaker_verification_status:string;speaker_verified:boolean|null;risk_score:number;risk_level:RiskResult['level'];decision:string;recommended_action?:string|null;reasons?:string[]}
 | {type:'risk_update';session_id:string;risk_score:number;risk_level:RiskResult['level'];decision:string}
 | ({type:'alert'} & SecurityAlert)
 | {type:'session_completed';session_id:string;segments_processed:number;highest_risk_score:number;final_risk_level:RiskResult['level'];timestamp:string}
 | {type:'error';code:string;message:string}
 | {type:'pong';timestamp:string}
