from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Revision(Base):
    __tablename__ = "revisions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        index=True
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    recall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="scheduled",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ------------------------------------------------------------
    # Relationship
    # ------------------------------------------------------------

    topic = relationship(
        "Topic",
        foreign_keys=[topic_id]
    )

    user = relationship(
        "User",
        foreign_keys=[user_id]
    )