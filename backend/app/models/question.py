from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Question(Base):
    __tablename__ = "questions"


    id: Mapped[int] = mapped_column(primary_key=True)

    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id"),
        nullable=False,
        index=True,
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        index=True,
    )

    # Optional subtopic
    subtopic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id"),
        nullable=True,
        index=True,
    )

    subject = relationship("Subject")
    topic = relationship(
        "Topic",
        foreign_keys=[topic_id],
    )
    subtopic = relationship(
        "Topic",
        foreign_keys=[subtopic_id],
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    option_a: Mapped[str | None] = mapped_column(Text)
    option_b: Mapped[str | None] = mapped_column(Text)
    option_c: Mapped[str | None] = mapped_column(Text)
    option_d: Mapped[str | None] = mapped_column(Text)

    correct_answer: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
    )

    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        String(30),
        default="MCQ",
        nullable=False,
    )

    is_pyq: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    exam_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    marks: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        nullable=False,
    )

    negative_marks: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )