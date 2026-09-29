# backend/app/services/diagnostic_mastery_service.py

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.models.diagnostic_answer import DiagnosticAnswer
from app.models.question import Question
from app.models.mastery import Mastery
from app.services.revision_service import RevisionService


class DiagnosticMasteryService:
    """
    Converts diagnostic assessment performance into initial topic mastery.

    Flow:
        Diagnostic Answers
              ↓
        Group by Topic
              ↓
        Calculate Accuracy
              ↓
        Calculate Average Time
              ↓
        Calculate Initial Mastery
              ↓
        Create / Update Mastery
              ↓
        Schedule Revision for weak topics
    """

    @staticmethod
    def calculate_initial_mastery(
        accuracy: float,
        total_questions: int,
    ) -> float:
        """
        Calculate conservative initial mastery.

        accuracy:
            Accuracy percentage from 0 to 100.

        total_questions:
            Number of diagnostic questions attempted/available
            for the topic.

        The coverage factor prevents a topic from being considered
        fully mastered from a very small number of questions.
        """

        if total_questions <= 0:
            return 0.0

        # More questions = more confidence in the diagnostic estimate.
        coverage_factor = min(1.0, total_questions / 3.0)

        # Center the estimate around 50.
        mastery = 50.0 + ((accuracy - 50.0) * coverage_factor)

        # Keep score between 0 and 100.
        mastery = max(0.0, min(100.0, mastery))

        return round(mastery, 2)

    @staticmethod
    def initialize_mastery(
        db: Session,
        user_id: int,
        session_id: int,
    ) -> list[dict[str, Any]]:
        """
        Generate initial mastery records from a completed diagnostic session.

        Returns:
            [
                {
                    "topic_id": ...,
                    "mastery_score": ...,
                    "accuracy": ...,
                    "attempts_count": ...,
                    "average_time_seconds": ...
                }
            ]
        """

        # ---------------------------------------------------------
        # 1. Fetch diagnostic answers for the session
        # ---------------------------------------------------------

        answers = (
            db.query(DiagnosticAnswer)
            .filter(
                DiagnosticAnswer.session_id == session_id
            )
            .all()
        )

        if not answers:
            return []

        # ---------------------------------------------------------
        # 2. Fetch all questions involved in the diagnostic
        # ---------------------------------------------------------

        question_ids = [
            answer.question_id
            for answer in answers
        ]

        questions = (
            db.query(Question)
            .filter(
                Question.id.in_(question_ids)
            )
            .all()
        )

        question_map = {
            question.id: question
            for question in questions
        }

        # ---------------------------------------------------------
        # 3. Group diagnostic answers by topic
        # ---------------------------------------------------------

        topic_data: dict[int, dict[str, Any]] = defaultdict(
            lambda: {
                "total": 0,
                "correct": 0,
                "time_total": 0,
            }
        )

        for answer in answers:

            question = question_map.get(answer.question_id)

            # Safety check in case a question was deleted.
            if question is None:
                continue

            topic_id = question.topic_id

            topic_data[topic_id]["total"] += 1

            if answer.is_correct:
                topic_data[topic_id]["correct"] += 1

            topic_data[topic_id]["time_total"] += (
                answer.time_taken_seconds or 0
            )

        # ---------------------------------------------------------
        # 4. Calculate mastery topic by topic
        # ---------------------------------------------------------

        mastery_results: list[dict[str, Any]] = []

        for topic_id, data in topic_data.items():

            total_questions = data["total"]
            correct_answers = data["correct"]
            total_time = data["time_total"]

            if total_questions <= 0:
                continue

            # Accuracy percentage
            accuracy = (
                correct_answers / total_questions
            ) * 100.0

            # Average time per question
            average_time = (
                total_time / total_questions
            )

            # Initial mastery
            mastery_score = (
                DiagnosticMasteryService.calculate_initial_mastery(
                    accuracy=accuracy,
                    total_questions=total_questions,
                )
            )

            # -----------------------------------------------------
            # 5. Find existing mastery record
            # -----------------------------------------------------

            mastery = (
                db.query(Mastery)
                .filter(
                    Mastery.user_id == user_id,
                    Mastery.topic_id == topic_id,
                )
                .first()
            )

            if mastery is None:

                # -------------------------------------------------
                # Create new mastery record
                # -------------------------------------------------

                mastery = Mastery(
                    user_id=user_id,
                    topic_id=topic_id,
                    mastery_score=mastery_score,
                    accuracy=round(accuracy, 2),
                    average_time_seconds=round(
                        average_time,
                        2,
                    ),
                    attempts_count=total_questions,
                    confidence_score=round(
                        accuracy,
                        2,
                    ),
                    forgetting_risk=0.0,
                )

                db.add(mastery)

            else:

                # -------------------------------------------------
                # Update existing mastery record
                # -------------------------------------------------

                mastery.mastery_score = mastery_score
                mastery.accuracy = round(
                    accuracy,
                    2,
                )
                mastery.average_time_seconds = round(
                    average_time,
                    2,
                )
                mastery.attempts_count = total_questions
                mastery.confidence_score = round(
                    accuracy,
                    2,
                )

                # Diagnostic is a fresh assessment,
                # so forgetting risk starts at 0.
                mastery.forgetting_risk = 0.0

            # -----------------------------------------------------
            # Store result for API response
            # -----------------------------------------------------

            mastery_results.append(
                {
                    "topic_id": topic_id,
                    "mastery_score": round(
                        mastery_score,
                        2,
                    ),
                    "accuracy": round(
                        accuracy,
                        2,
                    ),
                    "attempts_count": total_questions,
                    "average_time_seconds": round(
                        average_time,
                        2,
                    ),
                }
            )

        # ---------------------------------------------------------
        # 6. Save mastery records
        # ---------------------------------------------------------

        db.commit()

        # Refresh newly created/updated records
        for mastery in (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id
            )
            .all()
        ):
            db.refresh(mastery)

        # ---------------------------------------------------------
        # 7. Schedule revision for topics below 85 mastery
        # ---------------------------------------------------------

        for result in mastery_results:

            mastery_score = result["mastery_score"]

            # Topics below 85 are not considered mastered.
            if mastery_score < 85:

                RevisionService.schedule_revision(
                    db=db,
                    user_id=user_id,
                    topic_id=result["topic_id"],
                    mastery_score=mastery_score,
                )

        return mastery_results

    @staticmethod
    def get_topic_mastery(
        db: Session,
        user_id: int,
        topic_id: int,
    ) -> dict[str, Any] | None:
        """
        Get mastery information for a specific user/topic.
        """

        mastery = (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id,
                Mastery.topic_id == topic_id,
            )
            .first()
        )

        if mastery is None:
            return None

        return {
            "topic_id": mastery.topic_id,
            "mastery_score": mastery.mastery_score,
            "accuracy": mastery.accuracy,
            "attempts_count": mastery.attempts_count,
            "average_time_seconds": mastery.average_time_seconds,
            "confidence_score": mastery.confidence_score,
            "forgetting_risk": mastery.forgetting_risk,
        }

    @staticmethod
    def get_user_mastery(
        db: Session,
        user_id: int,
    ) -> list[dict[str, Any]]:
        """
        Get mastery information for all topics belonging to a user.
        """

        mastery_records = (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id
            )
            .order_by(
                Mastery.mastery_score.asc()
            )
            .all()
        )

        return [
            {
                "topic_id": mastery.topic_id,
                "mastery_score": mastery.mastery_score,
                "accuracy": mastery.accuracy,
                "attempts_count": mastery.attempts_count,
                "average_time_seconds": mastery.average_time_seconds,
                "confidence_score": mastery.confidence_score,
                "forgetting_risk": mastery.forgetting_risk,
            }
            for mastery in mastery_records
        ]