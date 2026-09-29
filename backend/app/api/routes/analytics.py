from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.api.dependencies import (
    get_current_user
)

from app.models.user import User

from app.services.mistake_service import (
    MistakeService
)

from app.services.recommendation_service import (
    RecommendationService
)

from app.schemas.analytics import (
    MistakeResponse,
    MistakeSummaryResponse,
    ReadinessDashboardResponse,
    ReadinessResponse,
    ReadinessTopic,
)

from app.services.readiness_service import ReadinessService

from app.schemas.analytics import NextActionResponse
from app.services.recommendation_service import RecommendationService

from app.schemas.analytics import (
    AdaptivePlanResponse,
    AdaptiveTopicPlan,
)

from app.services.adaptive_service import (
    AdaptiveService,
)

from app.services.mistake_service import MistakeService

from app.services.adaptive_service import AdaptiveService

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


# =====================================
# MISTAKE SUMMARY
# =====================================

@router.get("/mistakes")
def get_mistake_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    return MistakeService.get_mistake_summary(
        db=db,
        user_id=current_user.id,
    )


# =====================================
# NEXT BEST ACTION
# =====================================

@router.get("/next-action")
def get_next_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    return RecommendationService.get_next_action(
        db=db,
        user_id=current_user.id,
    )

@router.get(
    "/readiness/{exam_id}",
    response_model=ReadinessDashboardResponse,
)
def get_readiness(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:

        readiness = ReadinessService.calculate_readiness(
            db=db,
            user_id=current_user.id,
            exam_id=exam_id,
        )

        topics = ReadinessService.get_topic_analysis(
            db=db,
            user_id=current_user.id,
            exam_id=exam_id,
        )

        weak_topics = [
            topic
            for topic in topics
            if topic["mastery_score"] < 40
        ]

        strong_topics = [
            topic
            for topic in topics
            if topic["mastery_score"] >= 70
        ]

        return ReadinessDashboardResponse(
            readiness=ReadinessResponse(
                exam_id=exam_id,
                readiness_score=readiness.readiness_score,
                mastery_score=readiness.mastery_score,
                exam_performance_score=(
                    readiness.exam_performance_score
                ),
                accuracy_score=readiness.accuracy_score,
                speed_score=readiness.speed_score,
                consistency_score=(
                    readiness.consistency_score
                ),
                readiness_level=(
                    ReadinessService.get_readiness_level(
                        readiness.readiness_score
                    )
                ),
            ),
            topics=[
                ReadinessTopic(**topic)
                for topic in topics
            ],
            weak_topics=[
                ReadinessTopic(**topic)
                for topic in weak_topics
            ],
            strong_topics=[
                ReadinessTopic(**topic)
                for topic in strong_topics
            ],
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "/next-best-action",
    response_model=NextActionResponse,
)
def get_next_best_action(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return RecommendationService.get_next_action(
        db=db,
        user_id=current_user.id,
    )

@router.get(
    "/adaptive-plan/{exam_id}",
    response_model=AdaptivePlanResponse,
)
def get_adaptive_plan(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    plan = AdaptiveService.get_adaptive_plan(
        db=db,
        user_id=current_user.id,
        exam_id=exam_id,
    )

    return AdaptivePlanResponse(
        exam_id=exam_id,
        generated_at=datetime.utcnow().isoformat(),
        topics=[
            AdaptiveTopicPlan(**item)
            for item in plan
        ],
    )

@router.get(
    "/today-plan/{exam_id}",
    response_model=AdaptivePlanResponse,
)
def get_today_plan(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    plan = AdaptiveService.get_today_plan(
        db=db,
        user_id=current_user.id,
        exam_id=exam_id,
        limit=5,
    )

    return AdaptivePlanResponse(
        exam_id=exam_id,
        generated_at=datetime.utcnow().isoformat(),
        topics=[
            AdaptiveTopicPlan(**item)
            for item in plan
        ],
    )

@router.get(
    "/mistakes",
    response_model=list[MistakeResponse]
)
def get_mistakes(
    topic_id: int | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    mistakes = MistakeService.get_user_mistakes(
        db=db,
        user_id=current_user.id,
        topic_id=topic_id,
        limit=limit
    )

    return [
        MistakeResponse(
            id=mistake.id,
            question_id=mistake.question_id,
            topic_id=mistake.topic_id,
            mistake_type=mistake.mistake_type,
            explanation=mistake.explanation,
            created_at=mistake.created_at
        )
        for mistake in mistakes
    ]

@router.get(
    "/mistakes/summary",
    response_model=MistakeSummaryResponse
)
def get_mistake_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    summary = MistakeService.get_mistake_summary(
        db=db,
        user_id=current_user.id
    )

    most_common = (
        MistakeService.get_most_common_mistake(
            db=db,
            user_id=current_user.id
        )
    )

    total = sum(
        summary.values()
    )

    return MistakeSummaryResponse(
        total_mistakes=total,
        knowledge_gap=summary["KNOWLEDGE_GAP"],
        conceptual_error=summary["CONCEPTUAL_ERROR"],
        time_pressure=summary["TIME_PRESSURE"],
        careless_error=summary["CARELESS_ERROR"],
        wrong_approach=summary["WRONG_APPROACH"],
        most_common_mistake=(
            most_common["mistake_type"]
            if most_common
            else None
        )
    )

@router.get(
    "/adaptive-plan/{exam_id}",
    response_model=AdaptivePlanResponse
)
def get_adaptive_plan(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    plans = AdaptiveService.get_adaptive_plan(
        db=db,
        user_id=current_user.id,
        exam_id=exam_id
    )

    return AdaptivePlanResponse(
        exam_id=exam_id,
        generated_at=datetime.utcnow().isoformat(),
        topics=plans
    )

@router.get(
    "/today-plan/{exam_id}",
    response_model=AdaptivePlanResponse
)
def get_today_plan(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    plans = AdaptiveService.get_today_plan(
        db=db,
        user_id=current_user.id,
        exam_id=exam_id
    )

    return AdaptivePlanResponse(
        exam_id=exam_id,
        generated_at=datetime.utcnow().isoformat(),
        topics=plans
    )