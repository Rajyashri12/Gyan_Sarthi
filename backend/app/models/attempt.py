from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # =========================================================
    # USER
    # =========================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # =========================================================
    # EXAM SESSION
    # =========================================================

    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("exam_sessions.id"),
        nullable=True,
        index=True,
    )

    # =========================================================
    # QUESTION
    # =========================================================

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False,
        index=True,
    )

    # =========================================================
    # ANSWER
    # =========================================================

    selected_answer: Mapped[str | None] = mapped_column()

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    # =========================================================
    # PERFORMANCE
    # =========================================================

    time_taken_seconds: Mapped[float | None] = mapped_column(
        Float,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
    )

    # =========================================================
    # TIMESTAMP
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )