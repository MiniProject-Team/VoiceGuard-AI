import { useCallback, useState } from 'react'
import * as api from '../services/api'
import type { CreateSessionInput, Session } from '../types/session'
export function useSession(){const [session,setSession]=useState<Session|null>(null);const [loading,setLoading]=useState(false);const [error,setError]=useState<string|null>(null)
 const run=useCallback(async<T,>(task:()=>Promise<T>)=>{setLoading(true);setError(null);try{return await task()}catch(e){setError(e instanceof Error?e.message:'Request failed.');throw e}finally{setLoading(false)}},[])
 const create=useCallback(async(input:CreateSessionInput)=>{const created=await run(()=>api.createSession(input));const full=await api.getSession(created.session_id);setSession(full);return full},[run])
 const start=useCallback(async()=>{if(!session)return;await run(()=>api.startSession(session.session_id));setSession(await api.getSession(session.session_id))},[run,session])
 const stop=useCallback(async()=>{if(!session)return;await run(()=>api.stopSession(session.session_id));setSession(await api.getSession(session.session_id))},[run,session])
 const refresh=useCallback(async()=>{if(session)setSession(await run(()=>api.getSession(session.session_id)))},[run,session])
 const reset=useCallback(()=>{setSession(null);setError(null);setLoading(false)},[])
 return {session,setSession,loading,error,create,start,stop,refresh,reset}}
