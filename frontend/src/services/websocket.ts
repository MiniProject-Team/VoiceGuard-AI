import type { ServerMessage, WsState } from '../types/api'
import { WS_BASE_URL } from '../utils/constants'

interface Options { onMessage:(message:ServerMessage)=>void; onState:(state:WsState)=>void; onError:(message:string)=>void }
export class VoiceGuardSocket {
  private socket:WebSocket|null=null;private attempts=0;private intentional=false;private timer:number|undefined
  constructor(private sessionId:string,private options:Options,private maxAttempts=5){}
  connect(){this.intentional=false;this.options.onState(this.attempts?'reconnecting':'connecting');this.socket=new WebSocket(`${WS_BASE_URL}/sessions/${encodeURIComponent(this.sessionId)}`);this.socket.binaryType='arraybuffer';this.socket.onopen=()=>{this.attempts=0;this.options.onState('connected')};this.socket.onmessage=(event)=>{if(typeof event.data!=='string')return;try{this.options.onMessage(JSON.parse(event.data) as ServerMessage)}catch{this.options.onError('The backend sent an invalid WebSocket message.')}};this.socket.onerror=()=>this.options.onError('WebSocket connection error.');this.socket.onclose=()=>{this.socket=null;if(this.intentional){this.options.onState('disconnected');return}if(this.attempts>=this.maxAttempts){this.options.onState('failed');this.options.onError('Unable to reconnect.');return}this.attempts+=1;this.options.onState('reconnecting');this.timer=window.setTimeout(()=>this.connect(),Math.min(1000*2**(this.attempts-1),16000))}}
  send(type:'start'|'stop'|'ping'){if(this.socket?.readyState!==WebSocket.OPEN)throw new Error('WebSocket is not connected.');this.socket.send(JSON.stringify({type}))}
  sendAudio(pcm:ArrayBuffer){if(this.socket?.readyState!==WebSocket.OPEN)throw new Error('WebSocket is not connected.');this.socket.send(pcm)}
  disconnect(){this.intentional=true;if(this.timer)window.clearTimeout(this.timer);this.socket?.close();this.socket=null;this.options.onState('disconnected')}
}
