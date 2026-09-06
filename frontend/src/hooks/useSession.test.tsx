import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useSession } from './useSession'

const response = (body: unknown) => new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } })
const session = (id: string, status: 'created' | 'active' | 'completed') => ({ session_id: id, status, speaker_id: null, created_at: '2026-01-01T00:00:00Z', started_at: status === 'created' ? null : '2026-01-01T00:00:01Z', completed_at: status === 'completed' ? '2026-01-01T00:00:02Z' : null, segments_processed: 0, current_risk_score: 0, current_risk_level: 'UNKNOWN' })

afterEach(() => vi.unstubAllGlobals())
describe('useSession', () => {
  it('can clear a completed session and create a different replacement session', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(response({ session_id: 'SESSION_A', status: 'created', created_at: '2026-01-01T00:00:00Z' }))
      .mockResolvedValueOnce(response(session('SESSION_A', 'created')))
      .mockResolvedValueOnce(response({ session_id: 'SESSION_A', status: 'active' }))
      .mockResolvedValueOnce(response(session('SESSION_A', 'active')))
      .mockResolvedValueOnce(response({ session_id: 'SESSION_A', status: 'completed', segments_processed: 0, highest_risk_score: 0, final_risk_level: 'UNKNOWN' }))
      .mockResolvedValueOnce(response(session('SESSION_A', 'completed')))
      .mockResolvedValueOnce(response({ session_id: 'SESSION_B', status: 'created', created_at: '2026-01-01T00:01:00Z' }))
      .mockResolvedValueOnce(response(session('SESSION_B', 'created')))
    vi.stubGlobal('fetch', fetchMock)
    const { result } = renderHook(() => useSession())

    await act(async () => { await result.current.create({ context: {} }) })
    await act(async () => { await result.current.start() })
    await act(async () => { await result.current.stop() })
    expect(result.current.session?.status).toBe('completed')
    act(() => result.current.reset())
    expect(result.current.session).toBeNull()
    await act(async () => { await result.current.create({ context: {} }) })
    expect(result.current.session?.session_id).toBe('SESSION_B')
  })
})
