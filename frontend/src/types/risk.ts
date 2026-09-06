export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN'
export interface RiskResult { score:number; level:RiskLevel; decision:string; recommended_action?:string|null }
export interface SegmentResult { segment_id:number; synthetic_probability:number|null; speaker_similarity:number|null; risk_score:number|null; risk_level:RiskLevel; decision:string; recommended_action?:string|null }
export interface SecurityAlert { severity:string; alert_type:string; message:string; recommended_action:string; session_id?:string }
export interface TimelineEvent { id:string; timestamp:string; title:string; detail:string; level?:RiskLevel }
