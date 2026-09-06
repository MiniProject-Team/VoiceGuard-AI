import { isTerminalSession, type Session } from '../types/session'
import type { SecurityAlert, SegmentResult, TimelineEvent } from '../types/risk'
import { EmptyState } from '../components/common/EmptyState'
import { PageContainer } from '../components/layout/PageContainer'
import { RiskScoreCard } from '../components/dashboard/RiskScoreCard'
import { SyntheticVoiceCard } from '../components/dashboard/SyntheticVoiceCard'
import { SpeakerVerificationCard } from '../components/dashboard/SpeakerVerificationCard'
import { CallStatusCard } from '../components/dashboard/CallStatusCard'
import { RiskChart } from '../components/dashboard/RiskChart'
import { AlertPanel } from '../components/dashboard/AlertPanel'
import { AnalysisTimeline } from '../components/dashboard/AnalysisTimeline'
import { RecommendedAction } from '../components/dashboard/RecommendedAction'

interface Props {
  session: Session | null
  results: SegmentResult[]
  alerts: SecurityAlert[]
  events: TimelineEvent[]
  onLive: () => void
  onNewSession: () => void
}

export function Dashboard({ session, results, alerts, events, onLive, onNewSession }: Props) {
  if (!session) return <PageContainer title="Security overview" eyebrow="Command center" actions={<button className="btn-primary" onClick={onLive}>Start live analysis</button>}><EmptyState /></PageContainer>
  const latest = results.at(-1)
  const terminal = isTerminalSession(session.status)
  return <PageContainer title={terminal ? 'Last session' : 'Active session'} eyebrow="Command center" actions={terminal ? <button className="btn-primary" onClick={onNewSession}>New session</button> : undefined}>
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><RiskScoreCard score={latest?.risk_score ?? session.current_risk_score} level={latest?.risk_level ?? session.current_risk_level} /><SyntheticVoiceCard value={latest?.synthetic_probability ?? null} /><SpeakerVerificationCard value={latest?.speaker_similarity ?? null} /><CallStatusCard session={session} /></div>
    <div className="mt-4 grid gap-4 xl:grid-cols-[1.65fr_1fr]"><RiskChart results={results} /><AlertPanel alerts={alerts} /></div>
    <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_1.65fr]"><AnalysisTimeline events={events} /><RecommendedAction decision={latest?.decision ?? null} recommendation={latest?.recommended_action} level={latest?.risk_level ?? 'UNKNOWN'} /></div>
  </PageContainer>
}
