from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"),
        nullable=False,
        index=True
    )

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id"),
        nullable=False,
        index=True
    )

    mistake_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )