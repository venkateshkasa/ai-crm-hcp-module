"""
LangGraph ReAct agent orchestrating sales tools for HCP engagement.
Uses Groq (gemma2-9b-it) for reasoning; optional larger model via settings.groq_model_context.
"""
from __future__ import annotations

import datetime as dt
import json
import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from sqlalchemy.orm import Session

from app.models import FollowUp, HCP, Interaction
from app.services.llm import extract_interaction_fields, get_chat_model


SYSTEM_PROMPT = """You are an AI assistant for pharmaceutical / medtech field representatives using an HCP CRM.
You have tools to log and edit interactions, search HCPs, read interaction history, and schedule follow-ups.
When the user wants to record a visit, call log_interaction with raw_notes and hcp_id when known.
If they refer to an HCP by name, call search_hcp first to resolve the id.
Be concise in final answers; use tools for data changes and lookups.
Today (reference only): """ + dt.date.today().isoformat()


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    tool_trace: Annotated[list[dict[str, Any]], operator.add]


def build_tools(db: Session):
    @tool
    def log_interaction(
        hcp_id: int,
        raw_notes: str,
        channel: str = "in_person",
        occurred_at_iso: str | None = None,
    ) -> str:
        """Log a new HCP interaction. Uses the LLM to summarize notes and extract entities (topics, products, sentiment, next steps) before persisting."""
        hcp = db.get(HCP, hcp_id)
        if not hcp:
            return json.dumps({"error": f"HCP {hcp_id} not found"})
        extracted = extract_interaction_fields(raw_notes, hcp_name=hcp.name)
        occurred = (
            dt.datetime.fromisoformat(occurred_at_iso.replace("Z", "+00:00"))
            if occurred_at_iso
            else dt.datetime.now(dt.UTC)
        )
        row = Interaction(
            hcp_id=hcp_id,
            channel=channel,
            raw_notes=raw_notes,
            summary=extracted.summary,
            key_topics=extracted.key_topics,
            products_discussed=extracted.products_discussed,
            sentiment=extracted.sentiment,
            next_steps=extracted.next_steps,
            occurred_at=occurred,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return json.dumps(
            {
                "interaction_id": row.id,
                "summary": row.summary,
                "key_topics": row.key_topics,
                "products_discussed": row.products_discussed,
                "sentiment": row.sentiment,
                "next_steps": row.next_steps,
            }
        )

    @tool
    def edit_interaction(
        interaction_id: int,
        raw_notes: str | None = None,
        summary: str | None = None,
        channel: str | None = None,
        sentiment: str | None = None,
        next_steps: str | None = None,
        re_extract_from_notes: bool = False,
    ) -> str:
        """Modify an existing logged interaction. Set re_extract_from_notes=true to re-run LLM entity extraction when raw_notes change."""
        row = db.get(Interaction, interaction_id)
        if not row:
            return json.dumps({"error": f"Interaction {interaction_id} not found"})
        hcp = db.get(HCP, row.hcp_id)
        if raw_notes is not None:
            row.raw_notes = raw_notes
            if re_extract_from_notes:
                extracted = extract_interaction_fields(raw_notes, hcp_name=hcp.name if hcp else None)
                row.summary = extracted.summary
                row.key_topics = extracted.key_topics
                row.products_discussed = extracted.products_discussed
                row.sentiment = extracted.sentiment
                row.next_steps = extracted.next_steps
        if summary is not None:
            row.summary = summary
        if channel is not None:
            row.channel = channel
        if sentiment is not None:
            row.sentiment = sentiment
        if next_steps is not None:
            row.next_steps = next_steps
        db.commit()
        db.refresh(row)
        return json.dumps(
            {
                "interaction_id": row.id,
                "summary": row.summary,
                "key_topics": row.key_topics,
                "products_discussed": row.products_discussed,
                "sentiment": row.sentiment,
                "next_steps": row.next_steps,
            }
        )

    @tool
    def search_hcp(query: str, limit: int = 8) -> str:
        """Search healthcare professionals by name, specialty, institution, city, or state."""
        q = f"%{query.strip()}%"
        rows = (
            db.query(HCP)
            .filter(
                (HCP.name.ilike(q))
                | (HCP.specialty.ilike(q))
                | (HCP.institution.ilike(q))
                | (HCP.city.ilike(q))
                | (HCP.state.ilike(q))
            )
            .limit(limit)
            .all()
        )
        payload = [
            {
                "id": r.id,
                "name": r.name,
                "specialty": r.specialty,
                "institution": r.institution,
                "city": r.city,
                "state": r.state,
            }
            for r in rows
        ]
        return json.dumps({"matches": payload})

    @tool
    def get_interaction_history(hcp_id: int, limit: int = 10) -> str:
        """Retrieve recent logged interactions for an HCP, newest first."""
        rows = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.occurred_at.desc())
            .limit(limit)
            .all()
        )
        payload = [
            {
                "id": r.id,
                "channel": r.channel,
                "summary": r.summary,
                "occurred_at": r.occurred_at.isoformat(),
                "sentiment": r.sentiment,
            }
            for r in rows
        ]
        return json.dumps({"interactions": payload})

    @tool
    def schedule_follow_up(hcp_id: int, due_at_iso: str, note: str = "") -> str:
        """Schedule a follow-up task tied to an HCP (e.g., send study reprints, sample drop, advisory board invite)."""
        hcp = db.get(HCP, hcp_id)
        if not hcp:
            return json.dumps({"error": f"HCP {hcp_id} not found"})
        due = dt.datetime.fromisoformat(due_at_iso.replace("Z", "+00:00"))
        fu = FollowUp(hcp_id=hcp_id, due_at=due, note=note, status="open")
        db.add(fu)
        db.commit()
        db.refresh(fu)
        return json.dumps({"follow_up_id": fu.id, "due_at": fu.due_at.isoformat(), "note": fu.note})

    return [log_interaction, edit_interaction, search_hcp, get_interaction_history, schedule_follow_up]


def build_agent_graph(db: Session):
    tools = build_tools(db)
    tool_node = ToolNode(tools)
    model = get_chat_model().bind_tools(tools)

    def call_model(state: AgentState):
        msgs = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        resp = model.invoke(msgs)
        traces: list[dict[str, Any]] = []
        if isinstance(resp, AIMessage) and resp.tool_calls:
            for tc in resp.tool_calls:
                if isinstance(tc, dict):
                    traces.append({"phase": "tool_call", "name": tc.get("name"), "args": tc.get("args")})
                else:
                    traces.append({"phase": "tool_call", "name": getattr(tc, "name", None), "args": getattr(tc, "args", None)})
        return {"messages": [resp], "tool_trace": traces}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if isinstance(last, AIMessage) and last.tool_calls:
            return "tools"
        return END

    def tools_with_trace(state: AgentState):
        out = tool_node.invoke(state)
        traces: list[dict[str, Any]] = []
        for m in out.get("messages", []):
            if isinstance(m, ToolMessage):
                name = m.name or "tool"
                body = str(m.content)
                traces.append({"phase": "tool_result", "name": name, "content_preview": body[:1500]})
        merged: dict[str, Any] = dict(out)
        merged["tool_trace"] = traces
        return merged

    g = StateGraph(AgentState)
    g.add_node("agent", call_model)
    g.add_node("tools", tools_with_trace)
    g.set_entry_point("agent")
    g.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    g.add_edge("tools", "agent")
    return g.compile()


def run_agent_chat(db: Session, lc_messages: list[BaseMessage]) -> tuple[str, list[dict[str, Any]]]:
    graph = build_agent_graph(db)
    final = graph.invoke({"messages": list(lc_messages), "tool_trace": []})
    trace = list(final.get("tool_trace", []))
    out_msgs = final.get("messages", [])
    reply = ""
    for m in reversed(out_msgs):
        if isinstance(m, AIMessage) and m.content:
            reply = str(m.content)
            break
    if not reply and out_msgs:
        last = out_msgs[-1]
        reply = str(getattr(last, "content", "") or "")
    return reply, trace
