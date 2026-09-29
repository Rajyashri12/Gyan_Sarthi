from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(primary_key=True)

    session_id: Mapped[int] = mapped_column(
        ForeignKey("exam_sessions.id"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False,
        index=True,
    )

    selected_answer: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    marks_awarded: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    time_taken_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    answered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )