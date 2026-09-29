from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class ExamSessionQuestion(Base):
    __tablename__ = "exam_session_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

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