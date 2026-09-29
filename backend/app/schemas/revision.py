from datetime import datetime

from pydantic import BaseModel, Field


class RevisionScheduleRequest(BaseModel):

    topic_id: int

    recall_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class RevisionCompleteRequest(BaseModel):

    recall_score: float = Field(
        ...,
        ge=0,
        le=100,
    )


class RevisionResponse(BaseModel):

    revision_id: int

    topic_id: int

    topic: str

    scheduled_at: datetime

    recall_score: float | None

    status: str