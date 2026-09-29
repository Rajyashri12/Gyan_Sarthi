from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

from app.api.dependencies import get_current_user

from app.schemas.analytics import (
    RevisionResponse,
    RevisionCompleteRequest,
    RevisionCompleteResponse,
)

from app.services.revision_service import (
    RevisionService
)


router = APIRouter(
    prefix="/api/revision",
    tags=["Revision"]
)


# ================================================================
# DUE REVISIONS
# ================================================================

@router.get(
    "/due",
    response_model=list[RevisionResponse]
)
def get_due_revisions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    revisions = RevisionService.get_due_revisions(
        db=db,
        user_id=current_user.id
    )

    results = []

    for revision in revisions:

        topic = revision.topic

        results.append(
            RevisionResponse(
                revision_id=revision.id,
                topic_id=revision.topic_id,
                topic=(
                    topic.name
                    if topic
                    else "Unknown Topic"
                ),
                scheduled_at=revision.scheduled_at,
                mastery_score=0.0,
                forgetting_risk=0.0,
                mistake_count=0,
                priority_score=0.0,
                status=revision.status
            )
        )

    return results


# ================================================================
# REVISION DASHBOARD
# ================================================================

@router.get(
    "/dashboard",
    response_model=list[RevisionResponse]
)
def get_revision_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return RevisionService.get_revision_dashboard(
        db=db,
        user_id=current_user.id
    )


# ================================================================
# UPCOMING REVISIONS
# ================================================================

@router.get(
    "/upcoming",
    response_model=list[RevisionResponse]
)
def get_upcoming_revisions(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if days < 1:
        days = 1

    if days > 30:
        days = 30

    revisions = RevisionService.get_upcoming_revisions(
        db=db,
        user_id=current_user.id,
        days=days
    )

    results = []

    for revision in revisions:

        topic = revision.topic

        results.append(
            RevisionResponse(
                revision_id=revision.id,
                topic_id=revision.topic_id,
                topic=(
                    topic.name
                    if topic
                    else "Unknown Topic"
                ),
                scheduled_at=revision.scheduled_at,
                mastery_score=0.0,
                forgetting_risk=0.0,
                mistake_count=0,
                priority_score=0.0,
                status=revision.status
            )
        )

    return results


# ================================================================
# COMPLETE REVISION
# ================================================================

@router.post(
    "/{revision_id}/complete",
    response_model=RevisionCompleteResponse
)
def complete_revision(
    revision_id: int,
    request: RevisionCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:

        result = RevisionService.complete_revision(
            db=db,
            user_id=current_user.id,
            revision_id=revision_id,
            recall_score=request.recall_score
        )

        return RevisionCompleteResponse(
            revision_id=result["revision_id"],
            topic_id=result["topic_id"],
            recall_score=result["recall_score"],
            completed_at=result["completed_at"],
            next_revision_id=result["next_revision_id"],
            next_revision_at=result["next_revision_at"]
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )