import datetime as dt
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    specialty: Mapped[str] = mapped_column(String(128), default="")
    institution: Mapped[str] = mapped_column(String(255), default="")
    npi: Mapped[str | None] = mapped_column(String(32), nullable=True)
    city: Mapped[str] = mapped_column(String(128), default="")
    state: Mapped[str] = mapped_column(String(64), default="")

    interactions: Mapped[list["Interaction"]] = relationship(back_populates="hcp")
    follow_ups: Mapped[list["FollowUp"]] = relationship(back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hcp_id: Mapped[int] = mapped_column(ForeignKey("hcps.id"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(64), default="in_person")
    raw_notes: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    key_topics: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    products_discussed: Mapped[list[Any] | None] = mapped_column(JSON, nullable=True)
    sentiment: Mapped[str] = mapped_column(String(32), default="neutral")
    next_steps: Mapped[str] = mapped_column(Text, default="")
    occurred_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC)
    )

    hcp: Mapped["HCP"] = relationship(back_populates="interactions")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hcp_id: Mapped[int] = mapped_column(ForeignKey("hcps.id"), nullable=False, index=True)
    due_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    note: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="open")

    hcp: Mapped["HCP"] = relationship(back_populates="follow_ups")
