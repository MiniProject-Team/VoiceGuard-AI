from __future__ import annotations
import asyncio
from collections import defaultdict
from fastapi import WebSocket
from security.rate_limit import SlidingWindowRateLimiter

class ConnectionLimitError(RuntimeError): pass
class WebSocketManager:
    def __init__(self, max_connections: int = 100,connections_per_minute:int=60): self.max_connections = max_connections;self.connections_per_minute=connections_per_minute;self.rate_limiter=SlidingWindowRateLimiter(); self._connections: dict[str, set[WebSocket]] = defaultdict(set); self._lock = asyncio.Lock()
    @property
    def connection_count(self): return sum(map(len, self._connections.values()))
    async def connect(self, session_id: str, websocket: WebSocket):
        async with self._lock:
            if self.connection_count >= self.max_connections: raise ConnectionLimitError
            client=websocket.client.host if websocket.client else "unknown"
            if not self.rate_limiter.allow(f"ws:{client}",self.connections_per_minute):raise ConnectionLimitError
            await websocket.accept(); self._connections[session_id].add(websocket)
    async def disconnect(self, session_id: str, websocket: WebSocket):
        async with self._lock:
            self._connections[session_id].discard(websocket)
            if not self._connections[session_id]: self._connections.pop(session_id, None)
    async def send_to_session(self, session_id: str, message: dict):
        dead = []
        for socket in tuple(self._connections.get(session_id, ())):
            try: await socket.send_json(message)
            except Exception: dead.append(socket)
        for socket in dead: await self.disconnect(session_id, socket)
    async def broadcast(self, message: dict):
        for session_id in tuple(self._connections): await self.send_to_session(session_id, message)
