from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4
from security.audit import AuditLog

class SessionNotFound(KeyError): pass
class InvalidSessionState(ValueError): pass

@dataclass
class SessionRecord:
    session_id: str
    speaker_id: str | None
    context: dict
    status: str = "created"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    results: list[dict] = field(default_factory=list)
    current_risk_score: float = 0.0
    current_risk_level: str = "UNKNOWN"
    highest_risk_score: float = 0.0

class SessionRepository(Protocol):
    async def add(self, session: SessionRecord) -> None: ...
    async def get(self, session_id: str) -> SessionRecord | None: ...

class InMemorySessionRepository:
    def __init__(self): self._sessions: dict[str, SessionRecord] = {}; self._lock = asyncio.Lock()
    async def add(self, session: SessionRecord) -> None:
        async with self._lock: self._sessions[session.session_id] = session
    async def get(self, session_id: str) -> SessionRecord | None:
        async with self._lock: return self._sessions.get(session_id)
    async def all(self) -> list[SessionRecord]:
        async with self._lock: return list(self._sessions.values())
    async def delete(self, session_id: str) -> bool:
        async with self._lock: return self._sessions.pop(session_id, None) is not None

class SessionService:
    def __init__(self, repository: SessionRepository | None = None, max_active_sessions: int = 25, max_duration_seconds: int = 3600, audit: AuditLog | None = None):
        self.repository = repository or InMemorySessionRepository(); self._locks: dict[str, asyncio.Lock] = {}; self.max_active_sessions=max_active_sessions;self.max_duration_seconds=max_duration_seconds;self.audit=audit
    async def create(self, speaker_id: str | None, context: dict) -> SessionRecord:
        item = SessionRecord(f"SESSION_{uuid4().hex.upper()}", speaker_id, context); await self.repository.add(item); self._locks[item.session_id] = asyncio.Lock()
        if self.audit:self.audit.append("SESSION_CREATED",item.session_id)
        return item
    async def get(self, session_id: str) -> SessionRecord:
        item = await self.repository.get(session_id)
        if item is None: raise SessionNotFound(session_id)
        return item
    async def start(self, session_id: str) -> SessionRecord:
        item = await self.get(session_id)
        async with self._locks[session_id]:
            if item.status != "created": raise InvalidSessionState(f"Cannot start a {item.status} session.")
            active=sum(record.status=="active" for record in await self.repository.all())
            if active>=self.max_active_sessions:raise InvalidSessionState("Maximum active session limit reached.")
            item.status = "active"; item.started_at = datetime.now(timezone.utc)
            if hasattr(self,"monitoring"):self.monitoring.session_started()
            if self.audit:self.audit.append("SESSION_STARTED",item.session_id)
        return item
    async def stop(self, session_id: str) -> SessionRecord:
        item = await self.get(session_id)
        async with self._locks[session_id]:
            if item.status != "active": raise InvalidSessionState(f"Cannot stop a {item.status} session.")
            item.status = "stopping"; item.status = "completed"; item.completed_at = datetime.now(timezone.utc)
            if hasattr(self,"monitoring"):self.monitoring.session_completed()
            if self.audit:self.audit.append("SESSION_STOPPED",item.session_id,risk_score=item.highest_risk_score,risk_level=item.current_risk_level,decision=item.results[-1].get("decision") if item.results else None)
        return item
    async def fail(self, session_id: str) -> None:
        item = await self.get(session_id)
        if item.status == "active": item.status = "failed"; item.completed_at = datetime.now(timezone.utc)
    async def add_result(self, session_id: str, result: dict) -> None:
        item = await self.get(session_id)
        async with self._locks[session_id]:
            if item.started_at and (datetime.now(timezone.utc)-item.started_at).total_seconds()>self.max_duration_seconds:
                item.status="failed";item.completed_at=datetime.now(timezone.utc);raise InvalidSessionState("Maximum session duration exceeded.")
            item.results.append(result); score = float(result.get("risk_score") or 0); item.current_risk_score = score; item.current_risk_level = result.get("risk_level", "UNKNOWN"); item.highest_risk_score = max(item.highest_risk_score, score)
            if self.audit:self.audit.append("ANALYSIS_COMPLETED",item.session_id,**{key:value for key,value in result.items() if key!="session_id"})
    async def results(self, session_id: str, limit: int, offset: int) -> tuple[SessionRecord, list[dict]]:
        item = await self.get(session_id); return item, item.results[offset:offset + limit]
    async def delete(self,session_id:str)->bool:
        item=await self.get(session_id)
        if item.status in {"active","stopping"}:raise InvalidSessionState("Stop an active session before deletion.")
        deleted=await self.repository.delete(session_id);self._locks.pop(session_id,None)
        if deleted and self.audit:self.audit.append("SESSION_DELETED",session_id)
        return deleted
