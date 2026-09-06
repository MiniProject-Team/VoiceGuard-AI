import { LoaderCircle } from 'lucide-react'
export const LoadingState=({message='Loading…'}:{message?:string})=><div className="flex items-center gap-3 py-10 text-sm text-slate-400" role="status"><LoaderCircle className="h-4 w-4 animate-spin text-cyan"/>{message}</div>
