from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Readiness(Base):
    __tablename__ = "readiness"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id"),
        nullable=False,
        index=True,
    )

    readiness_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    mastery_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    exam_performance_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    accuracy_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    speed_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    consistency_score: Mapped[float] = mapped_column(
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