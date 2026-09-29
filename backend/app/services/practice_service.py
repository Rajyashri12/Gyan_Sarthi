# Gyan-Sarthi/backend/app/services/practice_service.py

from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.attempt import Attempt

from app.services.mistake_service import MistakeService
from app.services.mastery_service import MasteryService


class PracticeService:

    # ==========================================================
    # GET PRACTICE QUESTIONS
    # ==========================================================

    @staticmethod
    def get_questions(
        db: Session,
        subject_code: str | None = None,
        topic: str | None = None,
        difficulty: str | None = None,
        limit: int = 10,
    ):

        # ------------------------------------------------------
        # LIMIT PROTECTION
        # ------------------------------------------------------

        limit = max(1, min(limit, 50))

        # ------------------------------------------------------
        # BASE QUERY
        # ------------------------------------------------------

        query = db.query(Question)

        # ------------------------------------------------------
        # SUBJECT FILTER
        # ------------------------------------------------------

        if subject_code:

            query = (
                query
                .join(
                    Subject,
                    Question.subject_id == Subject.id,
                )
                .filter(
                    Subject.code
                    == subject_code.strip().upper()
                )
            )

        # ------------------------------------------------------
        # TOPIC FILTER
        # ------------------------------------------------------

        if topic:

            query = (
                query
                .join(
                    Topic,
                    Question.topic_id == Topic.id,
                )
                .filter(
                    Topic.name == topic.strip()
                )
            )

        # ------------------------------------------------------
        # DIFFICULTY FILTER
        # ------------------------------------------------------

        if difficulty:

            query = query.filter(
                Question.difficulty
                == difficulty.strip().lower()
            )

        # ------------------------------------------------------
        # FETCH QUESTIONS
        # ------------------------------------------------------

        questions = (
            query
            .order_by(Question.id)
            .limit(limit)
            .all()
        )

        return questions

    # ==========================================================
    # SUBMIT PRACTICE ANSWER
    # ==========================================================

    @staticmethod
    def submit_answer(
        db: Session,
        user_id: int,
        question_id: int,
        selected_answer: str,
        time_taken_seconds: int = 0,
        confidence: float | None = None,
    ):

        # ------------------------------------------------------
        # VALIDATE QUESTION
        # ------------------------------------------------------

        question = (
            db.query(Question)
            .filter(
                Question.id == question_id
            )
            .first()
        )

        if not question:
            raise ValueError(
                "Question not found."
            )

        # ------------------------------------------------------
        # NORMALIZE INPUT
        # ------------------------------------------------------

        selected = (
            selected_answer.strip().upper()
            if selected_answer
            else ""
        )

        correct = (
            question.correct_answer.strip().upper()
            if question.correct_answer
            else ""
        )

        # ------------------------------------------------------
        # VALIDATE ANSWER
        # ------------------------------------------------------

        is_correct = (
            selected == correct
        )

        # ------------------------------------------------------
        # NORMALIZE TIME
        # ------------------------------------------------------

        time_taken_seconds = max(
            0,
            int(time_taken_seconds or 0),
        )

        # ------------------------------------------------------
        # NORMALIZE CONFIDENCE
        # ------------------------------------------------------

        if confidence is not None:

            confidence = max(
                0.0,
                min(
                    float(confidence),
                    5.0,
                ),
            )

        # ------------------------------------------------------
        # CALCULATE MARKS
        # ------------------------------------------------------

        if is_correct:

            marks_awarded = (
                question.marks
            )

        else:

            marks_awarded = -(
                question.negative_marks
            )

        # ------------------------------------------------------
        # SAVE ATTEMPT
        # ------------------------------------------------------

        attempt = Attempt(
            user_id=user_id,
            question_id=question.id,
            selected_answer=selected,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
            confidence=confidence,
        )

        db.add(attempt)

        # ------------------------------------------------------
        # COMMIT ATTEMPT
        # ------------------------------------------------------

        db.commit()

        db.refresh(attempt)

        # ------------------------------------------------------
        # MISTAKE INTELLIGENCE
        # ------------------------------------------------------

        if not is_correct:

            try:

                MistakeService.record_mistake(
                    db=db,
                    user_id=user_id,
                    question_id=question.id,
                    topic_id=question.topic_id,
                    is_correct=is_correct,
                    time_taken_seconds=time_taken_seconds,
                    confidence=confidence,
                    question_type=question.question_type,
                )

            except Exception:

                # Mistake tracking should not prevent
                # the practice answer from being submitted.
                db.rollback()

        # ------------------------------------------------------
        # UPDATE TOPIC MASTERY
        # ------------------------------------------------------

        try:

            MasteryService.calculate_topic_mastery(
                db=db,
                user_id=user_id,
                topic_id=question.topic_id,
            )

        except Exception:

            # Mastery calculation failure should not
            # invalidate a successfully saved attempt.
            db.rollback()

        # ------------------------------------------------------
        # RESPONSE
        # ------------------------------------------------------

        return {
            "question_id": question.id,

            "selected_answer": selected,

            "correct_answer": correct,

            "is_correct": is_correct,

            "marks_awarded": marks_awarded,

            "explanation": question.explanation,
        }