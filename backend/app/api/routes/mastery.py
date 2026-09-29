from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.api.dependencies import (
    get_current_user
)

from app.models.user import User
from app.models.topic import Topic

from app.services.mastery_service import (
    MasteryService
)


router = APIRouter(
    prefix="/api/mastery",
    tags=["Mastery"],
)


@router.post(
    "/calculate/{topic_id}"
)
def calculate_mastery(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    topic = (
        db.query(Topic)
        .filter(
            Topic.id == topic_id
        )
        .first()
    )

    if not topic:

        raise HTTPException(
            status_code=404,
            detail="Topic not found.",
        )

    mastery = (
        MasteryService.calculate_topic_mastery(
            db=db,
            user_id=current_user.id,
            topic_id=topic_id,
        )
    )

    if not mastery:

        return {
            "message": (
                "No attempts found "
                "for this topic."
            )
        }

    level = (
        MasteryService.classify_mastery(
            mastery.mastery_score
        )
    )

    return {
        "topic_id": topic.id,

        "topic_name": topic.name,

        "mastery_score": (
            mastery.mastery_score
        ),

        "mastery_level": level,

        "accuracy": mastery.accuracy,

        "confidence_score": (
            mastery.confidence_score
        ),

        "average_time_seconds": (
            mastery.average_time_seconds
        ),

        "attempts_count": (
            mastery.attempts_count
        ),

        "forgetting_risk": (
            mastery.forgetting_risk
        ),
    }