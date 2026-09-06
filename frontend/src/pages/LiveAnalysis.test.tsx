import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { LiveAnalysis } from './LiveAnalysis'
import type { Session } from '../types/session'

const created: Session = { session_id: 'SESSION_A', status: 'created', speaker_id: null, created_at: '2026-01-01T00:00:00Z', started_at: null, completed_at: null, segments_processed: 0, current_risk_score: 0, current_risk_level: 'UNKNOWN' }
const active: Session = { ...created, status: 'active', started_at: '2026-01-01T00:00:01Z' }
const completed: Session = { ...created, status: 'completed', completed_at: '2026-01-01T00:01:00Z' }
const props = { results: [], alerts: [], events: [], ws: 'disconnected' as const, loading: false, error: null, onCreate: vi.fn().mockResolvedValue(undefined), onStart: vi.fn().mockResolvedValue(undefined), onStop: vi.fn().mockResolvedValue(undefined), onNewSession: vi.fn(), onUpload: vi.fn().mockResolvedValue(undefined) }

describe('LiveAnalysis session lifecycle', () => {
  it('shows an enabled create-session flow when no session exists', () => {
    render(<LiveAnalysis {...props} session={null} />)
    expect(screen.getByRole('button', { name: /create session/i })).toBeEnabled()
  })

  it('enables Start session only for a newly created session', () => {
    render(<LiveAnalysis {...props} session={created} />)
    expect(screen.getByRole('button', { name: /start session/i })).toBeEnabled()
    expect(screen.getByLabelText(/upload test wav/i)).toBeDisabled()
  })

  it('does not allow an already active session to be started again', () => {
    render(<LiveAnalysis {...props} session={active} />)
    expect(screen.getByRole('button', { name: /start session/i })).toBeDisabled()
    expect(screen.getByLabelText(/upload test wav/i)).toBeEnabled()
  })

  it('replaces terminal-session controls with New session', () => {
    const onNewSession = vi.fn()
    render(<LiveAnalysis {...props} session={completed} onNewSession={onNewSession} />)
    expect(screen.queryByRole('button', { name: /start session/i })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /new session/i }))
    expect(onNewSession).toHaveBeenCalledOnce()
  })
})
