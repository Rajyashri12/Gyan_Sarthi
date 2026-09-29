from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class DiagnosticSession(Base):
    __tablename__ = "diagnostic_sessions"

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

    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="in_progress",
        nullable=False,
    )

    score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    accuracy: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )