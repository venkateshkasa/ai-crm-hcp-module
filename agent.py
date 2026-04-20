from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas import AgentChatRequest, AgentChatResponse
from app.services.langgraph_agent import run_agent_chat

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(body: AgentChatRequest, db: Session = Depends(get_db)):
    if not settings.groq_api_key:
        return AgentChatResponse(
            reply=(
                "Agent is offline because GROQ_API_KEY is not configured. "
                "Add it to backend/.env and restart the API."
            ),
            tool_calls_trace=[],
        )
    lc_messages = []
    for m in body.messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        else:
            lc_messages.append(AIMessage(content=m.content))
    prefix = ""
    if body.hcp_id is not None:
        prefix = f"[Context: default HCP id {body.hcp_id}]\n"
    if prefix and lc_messages:
        first = lc_messages[0]
        if isinstance(first, HumanMessage):
            lc_messages[0] = HumanMessage(content=prefix + str(first.content))
    reply, trace = run_agent_chat(db, lc_messages)
    return AgentChatResponse(reply=reply, tool_calls_trace=trace)
