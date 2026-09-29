from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AILog(Base):
    __tablename__ = "ai_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response: Mapped[str | None] = mapped_column(
        Text,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
    )

    verification_score: Mapped[float | None] = mapped_column(
        Float,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )