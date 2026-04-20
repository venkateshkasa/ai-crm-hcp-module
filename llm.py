from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

from app.config import settings
from app.schemas import ExtractedInteraction


def get_chat_model(model: str | None = None) -> ChatGroq:
    mid = model or settings.groq_model
    return ChatGroq(
        model=mid,
        api_key=settings.groq_api_key or None,
        temperature=0.2,
    )


def extract_interaction_fields(raw_notes: str, hcp_name: str | None = None) -> ExtractedInteraction:
    """Use Groq LLM to summarize notes and extract CRM entities (larger context model by default)."""
    if not settings.groq_api_key:
        text = (raw_notes or "").strip()
        short = text[:280] if text else "Interaction logged without AI summary."
        return ExtractedInteraction(
            summary=short,
            key_topics=["general discussion"],
            products_discussed=[],
            sentiment="neutral",
            next_steps="Follow up based on HCP interest.",
        )

    try:
        model = get_chat_model(settings.groq_model_context).with_structured_output(ExtractedInteraction)
        ctx = f" HCP name: {hcp_name}." if hcp_name else ""
        prompt = (
            "You are a life sciences CRM assistant. From field rep notes after an HCP visit, "
            "produce a factual CRM record. Do not invent adverse events or claims; stick to what is implied in the notes."
            f"{ctx}\n\nNotes:\n{raw_notes}"
        )
        result: ExtractedInteraction = model.invoke(
            [SystemMessage(content="Extract structured CRM fields."), HumanMessage(content=prompt)]
        )
        return result
    except Exception:
        text = (raw_notes or "").strip()
        short = text[:280] if text else "Interaction logged; AI extraction failed."
        return ExtractedInteraction(
            summary=short,
            key_topics=["general discussion"],
            products_discussed=[],
            sentiment="neutral",
            next_steps="Retry AI extraction after confirming Groq setup.",
        )
