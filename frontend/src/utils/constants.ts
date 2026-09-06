export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace(/\/+$/, '')
export const WS_BASE_URL = (import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8000/ws/v1').replace(/\/+$/, '')
// Monitoring is exposed outside the versioned API routes.
export const API_ORIGIN_URL = new URL(API_BASE_URL).origin
export const MAX_CHART_POINTS = 1000
