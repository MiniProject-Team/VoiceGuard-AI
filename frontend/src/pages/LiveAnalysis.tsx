import { useState } from 'react'
import { FileAudio, Play, Plus, Radio, Square } from 'lucide-react'
import { isTerminalSession, type CreateSessionInput, type Session } from '../types/session'
import type { SecurityAlert, SegmentResult, TimelineEvent } from '../types/risk'
import type { WsState } from '../types/api'
import { PageContainer } from '../components/layout/PageContainer'
import { ErrorState } from '../components/common/ErrorState'
import { CallStatusCard } from '../components/dashboard/CallStatusCard'
import { RiskScoreCard } from '../components/dashboard/RiskScoreCard'
import { SyntheticVoiceCard } from '../components/dashboard/SyntheticVoiceCard'
import { SpeakerVerificationCard } from '../components/dashboard/SpeakerVerificationCard'
import { AlertPanel } from '../components/dashboard/AlertPanel'
import { AnalysisTimeline } from '../components/dashboard/AnalysisTimeline'
import { LoadingState } from '../components/common/LoadingState'

interface Props {
  session: Session | null
  results: SegmentResult[]
  alerts: SecurityAlert[]
  events: TimelineEvent[]
  ws: WsState
  loading: boolean
  error: string | null
  onCreate: (input: CreateSessionInput) => Promise<void>
  onStart: () => Promise<void>
  onStop: () => Promise<void>
  onNewSession: () => void
  onUpload: (file: File) => Promise<void>
}

export function LiveAnalysis(p: Props) {
  const [form, setForm] = useState({ speaker_id: '', call_origin: 'unknown', contact_match: false, transaction_amount: '', transaction_type: 'fund_transfer', privileged_action: false })
  const submit = (event: React.FormEvent) => {
    event.preventDefault()
    void p.onCreate({ speaker_id: form.speaker_id || undefined, context: { call_origin: form.call_origin, contact_match: form.contact_match, transaction_amount: form.transaction_amount ? Number(form.transaction_amount) : undefined, transaction_type: form.transaction_type, privileged_action: form.privileged_action } })
  }
  const latest = p.results.at(-1)
  const terminal = Boolean(p.session && isTerminalSession(p.session.status))

  return <PageContainer title="Live voice analysis" eyebrow="Demo mode · Uploaded audio" actions={p.session && <span className="text-xs uppercase tracking-wider text-slate-500">WebSocket: {p.ws}</span>}>
    {p.error && <div className="mb-4"><ErrorState message={p.error} /></div>}
    {!p.session ? <form onSubmit={submit} className="max-w-4xl rounded-xl border border-line bg-panel p-6">
      <div className="mb-6 flex items-center gap-3"><Plus className="text-cyan" /><div><h3 className="font-semibold text-white">Create analysis session</h3><p className="text-sm text-slate-500">Context is evaluated by the backend risk engine.</p></div></div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <label>Speaker ID<input value={form.speaker_id} onChange={event => setForm({ ...form, speaker_id: event.target.value })} placeholder="CEO_001" pattern="[A-Za-z0-9_.-]+" /></label>
        <label>Call origin<input value={form.call_origin} onChange={event => setForm({ ...form, call_origin: event.target.value })} /></label>
        <label>Transaction amount<input type="number" min="0" value={form.transaction_amount} onChange={event => setForm({ ...form, transaction_amount: event.target.value })} placeholder="500000" /></label>
        <label>Transaction type<input value={form.transaction_type} onChange={event => setForm({ ...form, transaction_type: event.target.value })} /></label>
        <label className="check"><input type="checkbox" checked={form.contact_match} onChange={event => setForm({ ...form, contact_match: event.target.checked })} /> Contact matches records</label>
        <label className="check"><input type="checkbox" checked={form.privileged_action} onChange={event => setForm({ ...form, privileged_action: event.target.checked })} /> Privileged action requested</label>
      </div>
      <button disabled={p.loading} className="btn-primary mt-6" type="submit"><Plus className="h-4 w-4" />Create session</button>
    </form> : <>
      <div className="mb-4 flex flex-wrap gap-3">
        {terminal ? <button className="btn-primary" onClick={p.onNewSession}><Plus className="h-4 w-4" />New session</button> : <>
          <button disabled={p.loading || p.session.status !== 'created'} className="btn-primary" onClick={() => void p.onStart()}><Play className="h-4 w-4" />Start session</button>
          <label className={`btn-secondary ${p.session.status !== 'active' ? 'pointer-events-none opacity-50' : ''}`}><FileAudio className="h-4 w-4" />Upload test WAV<input className="sr-only" type="file" accept=".wav,audio/wav" disabled={p.session.status !== 'active'} onChange={event => { const file = event.target.files?.[0]; if (file) void p.onUpload(file); event.target.value = '' }} /></label>
          <button disabled={p.loading || p.session.status !== 'active'} className="btn-danger" onClick={() => void p.onStop()}><Square className="h-4 w-4" />Stop session</button>
        </>}
        <span className="inline-flex items-center gap-2 rounded-lg border border-cyan/20 bg-cyan/5 px-3 text-xs text-cyan"><Radio className="h-4 w-4" />Audio is processed by VoiceGuard API; it is not stored in this browser.</span>
      </div>
      {p.loading && <LoadingState message="Communicating with VoiceGuard backend…" />}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><CallStatusCard session={p.session} /><RiskScoreCard score={latest?.risk_score ?? null} level={latest?.risk_level ?? 'UNKNOWN'} /><SyntheticVoiceCard value={latest?.synthetic_probability ?? null} /><SpeakerVerificationCard value={latest?.speaker_similarity ?? null} /></div>
      <div className="mt-4 grid gap-4 xl:grid-cols-2"><AlertPanel alerts={p.alerts} /><AnalysisTimeline events={p.events} /></div>
    </>}
  </PageContainer>
}
