import type { RiskLevel } from '../types/risk'
const styles:Record<RiskLevel,string>={LOW:'text-emerald-300 bg-emerald-400/10 border-emerald-400/30',MEDIUM:'text-yellow-300 bg-yellow-400/10 border-yellow-400/30',HIGH:'text-orange-300 bg-orange-400/10 border-orange-400/30',CRITICAL:'text-red-300 bg-red-500/10 border-red-500/40',UNKNOWN:'text-slate-300 bg-slate-400/10 border-slate-400/30'}
export const getRiskBadgeStyle=(level:RiskLevel)=>styles[level]
export const getRiskColor=(level:RiskLevel)=>({LOW:'#34d399',MEDIUM:'#facc15',HIGH:'#fb923c',CRITICAL:'#f87171',UNKNOWN:'#94a3b8'})[level]
export const getRiskLabel=(level:RiskLevel)=>level==='UNKNOWN'?'Awaiting analysis':level
