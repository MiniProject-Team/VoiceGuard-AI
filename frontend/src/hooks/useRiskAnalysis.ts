import { useCallback, useState } from 'react'
import type { ServerMessage } from '../types/api'
import type { RiskLevel, SecurityAlert, SegmentResult, TimelineEvent } from '../types/risk'
import { MAX_CHART_POINTS } from '../utils/constants'
import type { AnalysisResponse } from '../types/api'
export function useRiskAnalysis(){const [results,setResults]=useState<SegmentResult[]>([]);const [alerts,setAlerts]=useState<SecurityAlert[]>([]);const [events,setEvents]=useState<TimelineEvent[]>([]);const [lastUpdated,setLastUpdated]=useState<string|null>(null)
 const handle=useCallback((message:ServerMessage)=>{const timestamp='timestamp'in message?message.timestamp:new Date().toISOString();setLastUpdated(timestamp)
  if(message.type==='analysis_result'){const result:SegmentResult={segment_id:message.segment_id,synthetic_probability:message.synthetic_probability,speaker_similarity:message.speaker_similarity,risk_score:message.risk_score,risk_level:message.risk_level,decision:message.decision};setResults(old=>[...old,result].slice(-MAX_CHART_POINTS));setEvents(old=>[{id:`segment-${message.segment_id}-${timestamp}`,timestamp,title:`Segment ${message.segment_id} analyzed`,detail:`Risk ${message.risk_score}/100 · ${message.risk_level}`,level:message.risk_level},...old].slice(0,50))}
  if(message.type==='alert'){setAlerts(old=>[message,...old]);setEvents(old=>[{id:`alert-${timestamp}`,timestamp,title:`${message.severity.toUpperCase()} security alert`,detail:message.message,level:message.severity.toUpperCase() as RiskLevel},...old].slice(0,50))}
 },[])
 const ingestAnalysis=useCallback((response:AnalysisResponse)=>{const timestamp=new Date().toISOString();const result:SegmentResult={segment_id:response.segment_id,synthetic_probability:response.analysis.synthetic_probability,speaker_similarity:response.analysis.speaker_similarity,risk_score:response.risk.score,risk_level:response.risk.level,decision:response.risk.decision,recommended_action:response.risk.recommended_action};setResults(old=>[...old,result].slice(-MAX_CHART_POINTS));if(response.alert)setAlerts(old=>[response.alert!,...old]);setEvents(old=>[{id:`rest-${response.segment_id}-${timestamp}`,timestamp,title:`Segment ${response.segment_id} analyzed`,detail:`Risk ${response.risk.score}/100 · ${response.risk.level}`,level:response.risk.level},...old].slice(0,50));setLastUpdated(timestamp)},[])
 const reset=useCallback(()=>{setResults([]);setAlerts([]);setEvents([]);setLastUpdated(null)},[])
 return {results,setResults,alerts,events,lastUpdated,handle,ingestAnalysis,reset}}
