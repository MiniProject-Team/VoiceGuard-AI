from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ErrorDetail(StrictModel):
    code: str
    message: str
    request_id: str | None = None

class ErrorResponse(StrictModel):
    error: ErrorDetail

class MessageResponse(StrictModel):
    session_id: str
    status: str

class Components(BaseModel):
    model_config = ConfigDict(extra="allow")

class HealthResponse(StrictModel):
    status: str
    service: str = "voiceguard-api"
    version: str = "1.0.0"
    components: dict[str, str] | None = None
