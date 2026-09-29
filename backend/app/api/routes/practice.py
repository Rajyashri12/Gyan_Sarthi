from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.practice import (
    PracticeRequest,
    PracticeQuestionResponse,
    PracticeSubmitRequest,
    PracticeSubmitResponse,
)

from app.services.practice_service import (
    PracticeService
)

from app.api.dependencies import (
    get_current_user
)

from app.models.user import User

from app.schemas.practice import (
    AdaptivePracticeRequest,
    AdaptiveQuestionResponse,
)

from app.services.adaptive_question_service import (
    AdaptiveQuestionService,
)


router = APIRouter(
    prefix="/api/practice",
    tags=["Practice"],
)


# =====================================
# GET PRACTICE QUESTIONS
# =====================================

@router.post(
    "/questions",
    response_model=list[
        PracticeQuestionResponse
    ],
)
def get_practice_questions(
    request: PracticeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    questions = PracticeService.get_questions(
        db=db,
        subject_code=request.subject_code,
        topic=request.topic,
        difficulty=request.difficulty,
        limit=request.limit,
    )

    return questions


# =====================================
# SUBMIT ANSWER
# =====================================

@router.post(
    "/submit",
    response_model=PracticeSubmitResponse,
)
def submit_practice_answer(
    request: PracticeSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    try:

        result = PracticeService.submit_answer(
            db=db,
            user_id=current_user.id,
            question_id=request.question_id,
            selected_answer=request.selected_answer,
            time_taken_seconds=(
                request.time_taken_seconds
            ),
            confidence=request.confidence,
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@router.post(
    "/adaptive",
    response_model=list[AdaptiveQuestionResponse],
)
def adaptive_practice(
    request: AdaptivePracticeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    questions = (
        AdaptiveQuestionService
        .get_adaptive_questions(
            db=db,
            user_id=current_user.id,
            exam_id=request.exam_id,
            subject_code=request.subject_code,
            topic_id=request.topic_id,
            limit=request.limit,
        )
    )

    return [
        AdaptiveQuestionResponse(
            id=question.id,
            question_text=question.question_text,
            option_a=question.option_a,
            option_b=question.option_b,
            option_c=question.option_c,
            option_d=question.option_d,
            difficulty=question.difficulty,
            question_type=question.question_type,
            is_pyq=question.is_pyq,
            exam_year=question.exam_year,
            marks=question.marks,
            negative_marks=question.negative_marks,
            topic_id=question.topic_id,
        )
        for question in questions
    ]