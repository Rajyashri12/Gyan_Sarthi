from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Mastery(Base):

    __tablename__ = "mastery"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        index=True,
    )

    mastery_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    accuracy: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    average_time_seconds: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    attempts_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    forgetting_risk: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )