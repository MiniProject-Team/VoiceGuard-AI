import { WifiOff } from 'lucide-react'
import { StatusBadge } from '../common/StatusBadge'
import type { WsState } from '../../types/api'

export function Header({ backend, api, ai, ws, lastUpdated }: { backend: boolean | null; api: boolean | null; ai: boolean | null; ws: WsState; lastUpdated: string | null }) {
  return <header className="sticky top-0 z-20 border-b border-line bg-ink/95 px-5 py-4 backdrop-blur lg:px-8">
    <div className="flex flex-wrap items-center justify-between gap-3"><div><h1 className="font-semibold text-white">VoiceGuard AI Security Console</h1><p className="mt-0.5 text-xs text-slate-500">Real-Time Voice Impersonation Detection</p></div>
      <div className="flex flex-wrap items-center gap-2"><StatusBadge label={`Backend ${backend ? 'online' : backend === false ? 'offline' : 'checking'}`} tone={backend ? 'success' : backend === false ? 'danger' : 'neutral'} /><StatusBadge label={`API ${api ? 'online' : api === false ? 'offline' : 'checking'}`} tone={api ? 'success' : api === false ? 'danger' : 'neutral'} /><StatusBadge label={`AI ${ai ? 'ready' : ai === false ? 'unavailable' : 'checking'}`} tone={ai ? 'success' : ai === false ? 'danger' : 'neutral'} /><StatusBadge label={`Live ${ws}`} tone={ws === 'connected' ? 'success' : ws === 'failed' ? 'danger' : 'neutral'} />{ws !== 'connected' && <WifiOff className="h-4 w-4 text-slate-500" />}</div>
    </div>
    {lastUpdated && <p className="mt-2 text-right text-[11px] text-slate-600">Last result: {new Date(lastUpdated).toLocaleTimeString()}</p>}
  </header>
}
