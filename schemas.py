import datetime as dt
from typing import Any, Literal

from pydantic import BaseModel, Field


class HCPOut(BaseModel):
    id: int
    name: str
    specialty: str
    institution: str
    npi: str | None
    city: str
    state: str

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    hcp_id: int
    channel: str = "in_person"
    raw_notes: str
    occurred_at: dt.datetime | None = None


class InteractionOut(BaseModel):
    id: int
    hcp_id: int
    channel: str
    raw_notes: str
    summary: str
    key_topics: list[Any] | None
    products_discussed: list[Any] | None
    sentiment: str
    next_steps: str
    occurred_at: dt.datetime
    created_at: dt.datetime

    class Config:
        from_attributes = True


class InteractionPatch(BaseModel):
    channel: str | None = None
    raw_notes: str | None = None
    summary: str | None = None
    key_topics: list[Any] | None = None
    products_discussed: list[Any] | None = None
    sentiment: str | None = None
    next_steps: str | None = None
    occurred_at: dt.datetime | None = None


class ChatMessageIn(BaseModel):
    role: Literal["user", "assistant"] = "user"
    content: str


class AgentChatRequest(BaseModel):
    messages: list[ChatMessageIn]
    hcp_id: int | None = None


class AgentChatResponse(BaseModel):
    reply: str
    tool_calls_trace: list[dict[str, Any]] = []


class ExtractedInteraction(BaseModel):
    summary: str = Field(description="2-4 sentence clinical/commercial summary for CRM")
    key_topics: list[str] = Field(description="Short bullet topics discussed")
    products_discussed: list[str] = Field(description="Drug or device names mentioned")
    sentiment: str = Field(description="One of: positive, neutral, negative, mixed")
    next_steps: str = Field(description="Concrete follow-up actions for the rep")
