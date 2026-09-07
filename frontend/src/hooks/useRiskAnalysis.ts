import { useCallback, useState } from 'react'
import type { AnalysisResponse, ServerMessage } from '../types/api'
import type { RiskLevel, SecurityAlert, SegmentResult, TimelineEvent } from '../types/risk'
import { MAX_CHART_POINTS } from '../utils/constants'

export function useRiskAnalysis() {
  const [results, setResults] = useState<SegmentResult[]>([])
  const [alerts, setAlerts] = useState<SecurityAlert[]>([])
  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)
  const addEvent = (result: SegmentResult, timestamp: string, source: string) => {
    setEvents(old => [{ id: `${source}-${result.segment_id}-${timestamp}`, timestamp, title: `Segment ${result.segment_id} analyzed`, detail: `Risk ${result.risk_score}/100 - ${result.risk_level}`, level: result.risk_level }, ...old].slice(0, 50))
  }
  const handle = useCallback((message: ServerMessage) => {
    const timestamp = 'timestamp' in message ? message.timestamp : new Date().toISOString()
    setLastUpdated(timestamp)
    if (message.type === 'analysis_result') {
      const result: SegmentResult = { segment_id: message.segment_id, synthetic_probability: message.synthetic_probability, synthetic_detection_status: message.synthetic_detection_status, speaker_similarity: message.speaker_similarity, speaker_verification_status: message.speaker_verification_status, speaker_verified: message.speaker_verified, risk_score: message.risk_score, risk_level: message.risk_level, decision: message.decision, recommended_action: message.recommended_action, reasons: message.reasons }
      setResults(old => [...old, result].slice(-MAX_CHART_POINTS)); addEvent(result, timestamp, 'segment')
    }
    if (message.type === 'alert') {
      setAlerts(old => [message, ...old])
      setEvents(old => [{ id: `alert-${timestamp}`, timestamp, title: `${message.severity.toUpperCase()} security alert`, detail: message.message, level: message.severity.toUpperCase() as RiskLevel }, ...old].slice(0, 50))
    }
  }, [])
  const ingestAnalysis = useCallback((response: AnalysisResponse) => {
    const timestamp = new Date().toISOString()
    const result: SegmentResult = { segment_id: response.segment_id, synthetic_probability: response.analysis.synthetic_probability, synthetic_detection_status: response.analysis.synthetic_detection_status, speaker_similarity: response.analysis.speaker_similarity, speaker_verification_status: response.analysis.speaker_verification_status, speaker_verified: response.analysis.speaker_verified, risk_score: response.risk.score, risk_level: response.risk.level, decision: response.risk.decision, recommended_action: response.risk.recommended_action, reasons: response.risk.reasons }
    setResults(old => [...old, result].slice(-MAX_CHART_POINTS)); addEvent(result, timestamp, 'rest')
    if (response.alert) setAlerts(old => [response.alert!, ...old]); setLastUpdated(timestamp)
  }, [])
  const reset = useCallback(() => { setResults([]); setAlerts([]); setEvents([]); setLastUpdated(null) }, [])
  return { results, setResults, alerts, events, lastUpdated, handle, ingestAnalysis, reset }
}
