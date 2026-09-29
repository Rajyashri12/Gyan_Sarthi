from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user import User

from app.api.dependencies import get_current_user

from app.schemas.analytics import (
    DiagnosticStartRequest,
    DiagnosticStartResponse,
    DiagnosticQuestionResponse,
    DiagnosticAnswerRequest,
    DiagnosticAnswerResponse,
    DiagnosticResultResponse,
)

from app.services.diagnostic_service import (
    DiagnosticService,
)


router = APIRouter(
    prefix="/api/diagnostic",
    tags=["Diagnostic Assessment"],
)


# ================================================================
# START DIAGNOSTIC
# ================================================================

@router.post(
    "/start",
    response_model=DiagnosticStartResponse,
)
def start_diagnostic(
    request: DiagnosticStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        result = DiagnosticService.start_diagnostic(
            db=db,
            user_id=current_user.id,
            exam_id=request.exam_id,
            questions_per_subject=request.questions_per_subject,
        )

        session = result["session"]
        questions = result["questions"]

        response_questions = []

        for question in questions:

            subject_code = ""

            if question.subject:
                subject_code = question.subject.code

            response_questions.append(
                DiagnosticQuestionResponse(
                    id=question.id,
                    question_text=question.question_text,
                    option_a=question.option_a,
                    option_b=question.option_b,
                    option_c=question.option_c,
                    option_d=question.option_d,
                    difficulty=question.difficulty,
                    question_type=question.question_type,
                    marks=question.marks,
                    negative_marks=question.negative_marks,
                    subject_code=subject_code,
                    topic_id=question.topic_id,
                )
            )

        return DiagnosticStartResponse(
            session_id=session.id,
            exam_id=session.exam_id,
            total_questions=session.total_questions,
            started_at=session.started_at,
            questions=response_questions,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ================================================================
# SAVE ANSWER
# ================================================================

@router.post(
    "/{session_id}/answer",
    response_model=DiagnosticAnswerResponse,
)
def save_diagnostic_answer(
    session_id: int,
    request: DiagnosticAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        result = DiagnosticService.save_answer(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            question_id=request.question_id,
            selected_answer=request.selected_answer,
            time_taken_seconds=request.time_taken_seconds,
        )

        return DiagnosticAnswerResponse(
            session_id=result["session_id"],
            question_id=result["question_id"],
            selected_answer=result["selected_answer"],
            saved=result["saved"],
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ================================================================
# COMPLETE DIAGNOSTIC
# ================================================================

@router.post(
    "/{session_id}/complete",
    response_model=DiagnosticResultResponse,
)
def complete_diagnostic(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        result = DiagnosticService.complete_diagnostic(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )

        # ========================================================
        # IMPORTANT FIX
        #
        # DO NOT DO THIS:
        #
        # session = result["session"]
        #
        # The service now returns:
        #
        # result["session_id"]
        # result["exam_id"]
        # result["total_questions"]
        # etc.
        # ========================================================

        return DiagnosticResultResponse(
            session_id=result["session_id"],
            exam_id=result["exam_id"],
            total_questions=result["total_questions"],
            attempted=result["attempted"],
            correct=result["correct"],
            incorrect=result["incorrect"],
            unanswered=result["unanswered"],
            score=result["score"],
            accuracy=result["accuracy"],
            topic_results=result["topic_results"],
            initial_mastery=result.get(
                "initial_mastery",
                [],
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )