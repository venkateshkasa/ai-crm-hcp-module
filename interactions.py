import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HCP, Interaction
from app.schemas import InteractionCreate, InteractionOut, InteractionPatch
from app.services.llm import extract_interaction_fields

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.get("", response_model=list[InteractionOut])
def list_interactions(hcp_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Interaction).order_by(Interaction.occurred_at.desc())
    if hcp_id is not None:
        q = q.filter(Interaction.hcp_id == hcp_id)
    return q.limit(100).all()


@router.post("", response_model=InteractionOut)
def create_interaction(body: InteractionCreate, db: Session = Depends(get_db)):
    hcp = db.get(HCP, body.hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    extracted = extract_interaction_fields(body.raw_notes, hcp_name=hcp.name)
    occurred = body.occurred_at or dt.datetime.now(dt.UTC)
    row = Interaction(
        hcp_id=body.hcp_id,
        channel=body.channel,
        raw_notes=body.raw_notes,
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
    return row


@router.patch("/{interaction_id}", response_model=InteractionOut)
def patch_interaction(interaction_id: int, body: InteractionPatch, db: Session = Depends(get_db)):
    row = db.get(Interaction, interaction_id)
    if not row:
        raise HTTPException(status_code=404, detail="Interaction not found")
    hcp = db.get(HCP, row.hcp_id)
    data = body.model_dump(exclude_unset=True)
    if "raw_notes" in data and data["raw_notes"] is not None:
        row.raw_notes = data["raw_notes"]
        extracted = extract_interaction_fields(row.raw_notes, hcp_name=hcp.name if hcp else None)
        row.summary = extracted.summary
        row.key_topics = extracted.key_topics
        row.products_discussed = extracted.products_discussed
        row.sentiment = extracted.sentiment
        row.next_steps = extracted.next_steps
    for k in ("channel", "summary", "key_topics", "products_discussed", "sentiment", "next_steps", "occurred_at"):
        if k not in data:
            continue
        if k == "summary" and "raw_notes" in data:
            continue
        setattr(row, k, data[k])
    db.commit()
    db.refresh(row)
    return row
