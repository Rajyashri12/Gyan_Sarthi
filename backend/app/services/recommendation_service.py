from datetime import datetime

from sqlalchemy.orm import Session

from app.models.mastery import Mastery
from app.models.mistake import Mistake
from app.models.revision import Revision
from app.models.topic import Topic


class RecommendationService:

    @staticmethod
    def get_next_action(
        db: Session,
        user_id: int,
    ):

        now = datetime.utcnow()

        # -------------------------------------------------
        # 1. CHECK OVERDUE REVISION
        # -------------------------------------------------

        overdue_revision = (
            db.query(Revision)
            .filter(
                Revision.user_id == user_id,
                Revision.status == "scheduled",
                Revision.scheduled_at <= now,
            )
            .order_by(
                Revision.scheduled_at.asc()
            )
            .first()
        )

        if overdue_revision:

            topic = (
                db.query(Topic)
                .filter(
                    Topic.id == overdue_revision.topic_id
                )
                .first()
            )

            return {
                "action": "REVISE",
                "priority": 95.0,
                "topic_id": overdue_revision.topic_id,
                "topic": topic.name if topic else None,
                "reason": (
                    "This topic is due for revision."
                ),
                "recommended_questions": 5,
                "estimated_minutes": 15,
            }

        # -------------------------------------------------
        # 2. FIND WEAKEST TOPIC
        # -------------------------------------------------

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

        if not mastery_records:

            return {
                "action": "START_DIAGNOSTIC",
                "priority": 100.0,
                "topic_id": None,
                "topic": None,
                "reason": (
                    "No learning history is available yet. "
                    "Start a diagnostic assessment."
                ),
                "recommended_questions": 20,
                "estimated_minutes": 30,
            }

        weakest = mastery_records[0]

        topic = (
            db.query(Topic)
            .filter(
                Topic.id == weakest.topic_id
            )
            .first()
        )

        topic_name = (
            topic.name
            if topic
            else "Unknown Topic"
        )

        mastery_score = weakest.mastery_score

        # -------------------------------------------------
        # 3. VERY WEAK TOPIC
        # -------------------------------------------------

        if mastery_score < 40:

            return {
                "action": "CONCEPT_REVIEW",
                "priority": 90.0,
                "topic_id": weakest.topic_id,
                "topic": topic_name,
                "reason": (
                    f"Your mastery in {topic_name} "
                    f"is {mastery_score:.1f}%. "
                    "Review the concept before practicing."
                ),
                "recommended_questions": 5,
                "estimated_minutes": 20,
            }

        # -------------------------------------------------
        # 4. DEVELOPING TOPIC
        # -------------------------------------------------

        if mastery_score < 70:

            return {
                "action": "TARGETED_PRACTICE",
                "priority": 80.0,
                "topic_id": weakest.topic_id,
                "topic": topic_name,
                "reason": (
                    f"{topic_name} has "
                    f"{mastery_score:.1f}% mastery. "
                    "Targeted practice can strengthen it."
                ),
                "recommended_questions": 10,
                "estimated_minutes": 20,
            }

        # -------------------------------------------------
        # 5. STRONG TOPIC
        # -------------------------------------------------

        if mastery_score < 85:

            return {
                "action": "REVISION",
                "priority": 60.0,
                "topic_id": weakest.topic_id,
                "topic": topic_name,
                "reason": (
                    f"{topic_name} is developing well. "
                    "Revise and reinforce the topic."
                ),
                "recommended_questions": 5,
                "estimated_minutes": 15,
            }

        # -------------------------------------------------
        # 6. HIGH MASTERY
        # -------------------------------------------------

        return {
            "action": "MOCK_TEST",
            "priority": 50.0,
            "topic_id": weakest.topic_id,
            "topic": topic_name,
            "reason": (
                "Your tracked topics have strong mastery. "
                "Test your performance under exam conditions."
            ),
            "recommended_questions": 20,
            "estimated_minutes": 30,
        }