from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.schemas.exam import (
    ExamAnswerRequest,
    ExamAnswerResponse,
    ExamQuestionResponse,
    ExamResultResponse,
    ExamStartRequest,
    ExamStartResponse,
    TopicPerformance,
)
from app.services.exam_service import ExamService


router = APIRouter(
    prefix="/api/exam",
    tags=["Exam Simulation"],
)


@router.post(
    "/start",
    response_model=ExamStartResponse,
)
def start_exam(
    request: ExamStartRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:

        session, questions = ExamService.start_exam(
            db=db,
            user_id=current_user.id,
            exam_id=request.exam_id,
            total_questions=request.total_questions,
            duration_minutes=request.duration_minutes,
        )

        return ExamStartResponse(
            session_id=session.id,
            exam_id=session.exam_id,
            total_questions=session.total_questions,
            duration_minutes=session.duration_minutes,
            started_at=session.started_at,
            questions=[
                ExamQuestionResponse(
                    id=q.id,
                    question_text=q.question_text,
                    option_a=q.option_a,
                    option_b=q.option_b,
                    option_c=q.option_c,
                    option_d=q.option_d,
                    difficulty=q.difficulty,
                    question_type=q.question_type,
                    marks=q.marks,
                    negative_marks=q.negative_marks,
                    topic_id=q.topic_id,
                )
                for q in questions
            ],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/{session_id}/answer",
    response_model=ExamAnswerResponse,
)
def save_answer(
    session_id: int,
    request: ExamAnswerRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:

        answer = ExamService.save_answer(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            question_id=request.question_id,
            selected_answer=request.selected_answer,
            time_taken_seconds=request.time_taken_seconds,
        )

        return ExamAnswerResponse(
            session_id=session_id,
            question_id=answer.question_id,
            selected_answer=answer.selected_answer,
            saved=True,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/{session_id}/submit",
    response_model=ExamResultResponse,
)
def submit_exam(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    try:

        result = ExamService.submit_exam(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )

        session = result["session"]

        topic_performance = (
            ExamService.get_topic_performance(
                db=db,
                session_id=session_id,
            )
        )

        return ExamResultResponse(
            session_id=session.id,
            exam_id=session.exam_id,
            total_questions=session.total_questions,
            attempted=result["attempted"],
            correct=result["correct"],
            incorrect=result["incorrect"],
            unanswered=result["unanswered"],
            total_marks=round(
                session.total_marks,
                2,
            ),
            score=round(
                session.score,
                2,
            ),
            accuracy=round(
                session.accuracy,
                2,
            ),
            duration_minutes=session.duration_minutes,
            time_used_seconds=result["time_used"],
            topic_performance=[
                TopicPerformance(**item)
                for item in topic_performance
            ],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )