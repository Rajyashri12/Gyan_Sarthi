from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.mistake import Mistake
from app.models.question import Question


class MistakeService:

    # ============================================================
    # DETECT MISTAKE TYPE
    # ============================================================

    @staticmethod
    def detect_mistake_type(
        question: Question,
        is_correct: bool,
        time_taken_seconds: int = 0,
        confidence: float | None = None
    ) -> str:
        """
        Determine the likely reason for an incorrect answer.

        This is an MVP rule-based classifier.
        """

        # --------------------------------------------------------
        # Correct answer
        # --------------------------------------------------------

        if is_correct:
            return "NONE"

        # --------------------------------------------------------
        # Very long solving time
        # --------------------------------------------------------

        if time_taken_seconds >= 120:

            return "TIME_PRESSURE"

        # --------------------------------------------------------
        # Low confidence + incorrect
        # --------------------------------------------------------

        if (
            confidence is not None
            and confidence < 0.35
        ):

            return "KNOWLEDGE_GAP"

        # --------------------------------------------------------
        # MCQ conceptual mistake
        # --------------------------------------------------------

        if question.question_type.upper() == "MCQ":

            return "CONCEPTUAL_ERROR"

        # --------------------------------------------------------
        # Default
        # --------------------------------------------------------

        return "KNOWLEDGE_GAP"

    # ============================================================
    # GENERATE EXPLANATION
    # ============================================================

    @staticmethod
    def generate_mistake_explanation(
        mistake_type: str
    ) -> str:

        explanations = {

            "KNOWLEDGE_GAP":
                "The answer suggests that the underlying concept may not be fully understood.",

            "CONCEPTUAL_ERROR":
                "The answer appears to indicate a misunderstanding or incorrect application of the concept.",

            "TIME_PRESSURE":
                "The question was answered incorrectly after spending significant time on it. Timed practice may help.",

            "CARELESS_ERROR":
                "The concept may be known, but the answer appears to contain an avoidable mistake.",

            "WRONG_APPROACH":
                "The selected approach may not have been appropriate for solving the question.",

            "NONE":
                "No mistake detected."
        }

        return explanations.get(
            mistake_type,
            "The answer was incorrect and requires further analysis."
        )

    # ============================================================
    # RECORD MISTAKE
    # ============================================================

    @staticmethod
    def record_mistake(
        db: Session,
        user_id: int,
        question: Question,
        is_correct: bool,
        time_taken_seconds: int = 0,
        confidence: float | None = None
    ):

        # --------------------------------------------------------
        # Correct answer → no mistake
        # --------------------------------------------------------

        if is_correct:
            return None

        # --------------------------------------------------------
        # Determine mistake
        # --------------------------------------------------------

        mistake_type = MistakeService.detect_mistake_type(
            question=question,
            is_correct=is_correct,
            time_taken_seconds=time_taken_seconds,
            confidence=confidence
        )

        explanation = (
            MistakeService.generate_mistake_explanation(
                mistake_type
            )
        )

        # --------------------------------------------------------
        # Save mistake
        # --------------------------------------------------------

        mistake = Mistake(
            user_id=user_id,
            question_id=question.id,
            topic_id=question.topic_id,
            mistake_type=mistake_type,
            explanation=explanation
        )

        db.add(mistake)
        db.commit()
        db.refresh(mistake)

        return mistake

    # ============================================================
    # GET USER MISTAKES
    # ============================================================

    @staticmethod
    def get_user_mistakes(
        db: Session,
        user_id: int,
        topic_id: int | None = None,
        limit: int = 50
    ):

        query = (
            db.query(Mistake)
            .filter(
                Mistake.user_id == user_id
            )
        )

        if topic_id is not None:

            query = query.filter(
                Mistake.topic_id == topic_id
            )

        return (
            query
            .order_by(
                Mistake.created_at.desc()
            )
            .limit(limit)
            .all()
        )

    # ============================================================
    # MISTAKE COUNTS BY TYPE
    # ============================================================

    @staticmethod
    def get_mistake_summary(
        db: Session,
        user_id: int
    ):

        rows = (
            db.query(
                Mistake.mistake_type,
                func.count(Mistake.id)
            )
            .filter(
                Mistake.user_id == user_id
            )
            .group_by(
                Mistake.mistake_type
            )
            .all()
        )

        summary = {
            "KNOWLEDGE_GAP": 0,
            "CONCEPTUAL_ERROR": 0,
            "TIME_PRESSURE": 0,
            "CARELESS_ERROR": 0,
            "WRONG_APPROACH": 0
        }

        for mistake_type, count in rows:

            summary[mistake_type] = count

        return summary

    # ============================================================
    # TOPIC MISTAKE COUNT
    # ============================================================

    @staticmethod
    def get_topic_mistake_count(
        db: Session,
        user_id: int,
        topic_id: int
    ):

        return (
            db.query(Mistake)
            .filter(
                Mistake.user_id == user_id,
                Mistake.topic_id == topic_id
            )
            .count()
        )

    # ============================================================
    # MOST COMMON MISTAKE
    # ============================================================

    @staticmethod
    def get_most_common_mistake(
        db: Session,
        user_id: int
    ):

        result = (
            db.query(
                Mistake.mistake_type,
                func.count(Mistake.id).label("count")
            )
            .filter(
                Mistake.user_id == user_id
            )
            .group_by(
                Mistake.mistake_type
            )
            .order_by(
                func.count(Mistake.id).desc()
            )
            .first()
        )

        if not result:
            return None

        return {
            "mistake_type": result.mistake_type,
            "count": result.count
        }