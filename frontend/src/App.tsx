import { useCallback, useEffect, useState } from 'react'
import { Sidebar, type Page } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { Dashboard } from './pages/Dashboard'
import { LiveAnalysis } from './pages/LiveAnalysis'
import { Sessions } from './pages/Sessions'
import { SessionDetails } from './pages/SessionDetails'
import { SystemStatus } from './pages/SystemStatus'
import { About } from './pages/About'
import { Governance } from './pages/Governance'
import { useSession } from './hooks/useSession'
import { useRiskAnalysis } from './hooks/useRiskAnalysis'
import { useWebSocket } from './hooks/useWebSocket'
import * as api from './services/api'
import type { HealthResponse, MonitoringSummary, ServerMessage } from './types/api'
import { isTerminalSession, type CreateSessionInput, type Session } from './types/session'
import type { SegmentResult } from './types/risk'

const errorMessage = (result: PromiseSettledResult<unknown>) => result.status === 'rejected' && result.reason instanceof Error ? result.reason.message : 'Backend status unavailable.'

export default function App() {
  const [page, setPage] = useState<Page>('dashboard')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [readiness, setReadiness] = useState<HealthResponse | null>(null)
  const [monitoring, setMonitoring] = useState<MonitoringSummary | null>(null)
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [known, setKnown] = useState<Session[]>([])
  const [details, setDetails] = useState<{ session: Session; results: SegmentResult[] } | null>(null)
  const sessionHook = useSession()
  const risk = useRiskAnalysis()
  const onMessage = useCallback((message: ServerMessage) => {
    risk.handle(message)
    if (message.type === 'session_completed') void sessionHook.refresh()
  }, [risk.handle, sessionHook.refresh])
  const socket = useWebSocket(sessionHook.session?.session_id ?? null, onMessage)

  const checkStatus = useCallback(async () => {
    const [liveResult, healthResult, readyResult, monitoringResult] = await Promise.allSettled([api.livenessCheck(), api.healthCheck(), api.readinessCheck(), api.monitoringSummary()])
    setBackendOnline(liveResult.status === 'fulfilled')
    setApiOnline(healthResult.status === 'fulfilled')
    setHealth(healthResult.status === 'fulfilled' ? healthResult.value : null)
    setReadiness(readyResult.status === 'fulfilled' ? readyResult.value : null)
    setMonitoring(monitoringResult.status === 'fulfilled' ? monitoringResult.value : null)
    const failed = [liveResult, healthResult, readyResult].filter(result => result.status === 'rejected')
    setStatusError(failed.length ? errorMessage(failed[0]) : null)
  }, [])

  useEffect(() => {
    void checkStatus()
    const timer = window.setInterval(() => void checkStatus(), 15000)
    return () => window.clearInterval(timer)
  }, [checkStatus])

  useEffect(() => {
    if (sessionHook.session && isTerminalSession(sessionHook.session.status)) socket.disconnect()
  }, [sessionHook.session?.session_id, sessionHook.session?.status, socket.disconnect])

  const resetLiveSession = useCallback(() => {
    socket.disconnect()
    socket.clearError()
    risk.reset()
    sessionHook.reset()
    setDetails(null)
    setPage('live')
  }, [risk.reset, sessionHook.reset, socket.clearError, socket.disconnect])

  const create = async (input: CreateSessionInput) => {
    try {
      risk.reset()
      const item = await sessionHook.create(input)
      setKnown(old => [item, ...old.filter(session => session.session_id !== item.session_id)])
    } catch { /* surfaced by useSession */ }
  }
  const start = async () => {
    try {
      await sessionHook.start()
      socket.connect()
    } catch { /* surfaced by useSession */ }
  }
  const stop = async () => {
    const sessionId = sessionHook.session?.session_id
    if (!sessionId) return
    try {
      await sessionHook.stop()
      socket.disconnect()
      const updated = await api.getSession(sessionId)
      sessionHook.setSession(updated)
      setKnown(old => old.map(session => session.session_id === updated.session_id ? updated : session))
    } catch { /* surfaced by useSession */ }
  }
  const upload = async (file: File) => {
    const sessionId = sessionHook.session?.session_id
    if (!sessionId || sessionHook.session?.status !== 'active') return
    try {
      const response = await api.analyzeAudio(sessionId, file)
      risk.ingestAnalysis(response)
      await sessionHook.refresh()
    } catch { /* surfaced by future status refresh */ }
  }
  const select = async (item: Session) => {
    try {
      const [session, rows] = await Promise.all([api.getSession(item.session_id), api.getSessionResults(item.session_id)])
      setDetails({ session, results: rows.results })
      setPage('sessions')
    } catch { /* Sessions remains usable */ }
  }
  const openLive = () => {
    if (sessionHook.session && isTerminalSession(sessionHook.session.status)) resetLiveSession()
    else setPage('live')
  }

  const content = details && page === 'sessions' ? <SessionDetails session={details.session} results={details.results} onBack={() => setDetails(null)} />
    : page === 'dashboard' ? <Dashboard session={sessionHook.session} results={risk.results} alerts={risk.alerts} events={risk.events} onLive={openLive} onNewSession={resetLiveSession} />
      : page === 'live' ? <LiveAnalysis session={sessionHook.session} results={risk.results} alerts={risk.alerts} events={risk.events} ws={socket.state} loading={sessionHook.loading} error={sessionHook.error ?? socket.error} onCreate={create} onStart={start} onStop={stop} onNewSession={resetLiveSession} onUpload={upload} />
        : page === 'sessions' ? <Sessions sessions={known} onSelect={item => void select(item)} />
          : page === 'governance' ? <Governance />
            : page === 'status' ? <SystemStatus health={health} readiness={readiness} monitoring={monitoring} ws={socket.state} error={statusError} onRefresh={() => void checkStatus()} />
              : <About />

  return <div className="min-h-screen bg-ink text-slate-200"><Sidebar page={page} onChange={next => { setDetails(null); setPage(next) }} /><div className="lg:pl-64"><Header backend={backendOnline} api={apiOnline} ai={readiness ? readiness.status === 'ready' : null} ws={socket.state} lastUpdated={risk.lastUpdated} />{content}</div></div>
}
