export const percent=(value:number|null|undefined)=>value==null?'—':`${Math.round(value*100)}%`
export const shortId=(id:string)=>id.length>12?`${id.slice(0,8)}…${id.slice(-4)}`:id
export const formatDate=(value:string|null)=>value?new Intl.DateTimeFormat(undefined,{dateStyle:'medium',timeStyle:'short'}).format(new Date(value)):'—'
export const duration=(started:string|null,ended?:string|null)=>{if(!started)return '00:00';const seconds=Math.max(0,Math.floor((new Date(ended??Date.now()).getTime()-new Date(started).getTime())/1000));return `${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`}
