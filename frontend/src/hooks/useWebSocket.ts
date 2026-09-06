import { useCallback, useEffect, useRef, useState } from 'react'
import { VoiceGuardSocket } from '../services/websocket'
import type { ServerMessage, WsState } from '../types/api'

export function useWebSocket(sessionId:string|null,onMessage:(message:ServerMessage)=>void){
  const [state,setState]=useState<WsState>('disconnected');const [error,setError]=useState<string|null>(null);const client=useRef<VoiceGuardSocket|null>(null);const handler=useRef(onMessage);handler.current=onMessage
  const connect=useCallback(()=>{if(!sessionId)return;client.current?.disconnect();client.current=new VoiceGuardSocket(sessionId,{onMessage:m=>handler.current(m),onState:setState,onError:setError});client.current.connect()},[sessionId])
  const disconnect=useCallback(()=>client.current?.disconnect(),[])
  const send=useCallback((type:'start'|'stop'|'ping')=>client.current?.send(type),[])
  const sendAudio=useCallback((data:ArrayBuffer)=>client.current?.sendAudio(data),[])
  useEffect(()=>()=>client.current?.disconnect(),[sessionId])
  return {state,error,connect,disconnect,send,sendAudio,clearError:()=>setError(null)}
}
