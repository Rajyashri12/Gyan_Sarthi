from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.revision import Revision
from app.models.mastery import Mastery
from app.models.mistake import Mistake
from app.models.topic import Topic


class RevisionService:

    # ============================================================
    # REVISION INTERVAL
    # ============================================================

    @staticmethod
    def calculate_interval(
        mastery_score: float,
        recall_score: float | None = None
    ) -> int:
        """
        Calculate the number of days before the next revision.

        Lower mastery / lower recall = shorter interval.
        """

        if recall_score is not None:

            effective_score = (
                mastery_score * 0.6
                + recall_score * 0.4
            )

        else:

            effective_score = mastery_score

        if effective_score < 40:
            return 1

        if effective_score < 60:
            return 2

        if effective_score < 75:
            return 4

        if effective_score < 90:
            return 7

        return 14

    # ============================================================
    # REVISION PRIORITY
    # ============================================================

    @staticmethod
    def calculate_priority(
        mastery_score: float,
        forgetting_risk: float,
        mistake_count: int = 0,
        days_since_revision: float = 0
    ) -> float:
        """
        Calculate revision priority.

        Higher score = revision should happen sooner.
        """

        mastery_weakness = (
            100.0 - mastery_score
        ) / 100.0

        forgetting = (
            forgetting_risk / 100.0
        )

        mistake_pressure = min(
            mistake_count / 5.0,
            1.0
        )

        # --------------------------------------------------------
        # How long since previous revision?
        # --------------------------------------------------------

        time_pressure = min(
            days_since_revision / 14.0,
            1.0
        )

        priority = (
            mastery_weakness * 0.35
            + forgetting * 0.30
            + mistake_pressure * 0.20
            + time_pressure * 0.15
        )

        return round(
            priority * 100,
            2
        )

    # ============================================================
    # GET NEXT REVISION DATE
    # ============================================================

    @staticmethod
    def calculate_next_revision_date(
        mastery_score: float,
        recall_score: float | None = None
    ) -> datetime:

        interval = (
            RevisionService.calculate_interval(
                mastery_score=mastery_score,
                recall_score=recall_score
            )
        )

        return datetime.utcnow() + timedelta(
            days=interval
        )

    # ============================================================
    # SCHEDULE REVISION
    # ============================================================

    @staticmethod
    def schedule_revision(
        db: Session,
        user_id: int,
        topic_id: int,
        mastery_score: float,
        recall_score: float | None = None
    ):

        scheduled_at = (
            RevisionService.calculate_next_revision_date(
                mastery_score=mastery_score,
                recall_score=recall_score
            )
        )

        # --------------------------------------------------------
        # Check for an existing pending revision
        # --------------------------------------------------------

        existing = (
            db.query(Revision)
            .filter(
                Revision.user_id == user_id,
                Revision.topic_id == topic_id,
                Revision.status == "scheduled"
            )
            .order_by(
                Revision.scheduled_at.asc()
            )
            .first()
        )

        if existing:

            existing.scheduled_at = scheduled_at

            if recall_score is not None:
                existing.recall_score = recall_score

            db.commit()
            db.refresh(existing)

            return existing

        # --------------------------------------------------------
        # Create revision
        # --------------------------------------------------------

        revision = Revision(
            user_id=user_id,
            topic_id=topic_id,
            scheduled_at=scheduled_at,
            completed_at=None,
            recall_score=recall_score,
            status="scheduled"
        )

        db.add(revision)
        db.commit()
        db.refresh(revision)

        return revision

    # ============================================================
    # COMPLETE REVISION
    # ============================================================

    @staticmethod
    def complete_revision(
        db: Session,
        user_id: int,
        revision_id: int,
        recall_score: float
    ):

        revision = (
            db.query(Revision)
            .filter(
                Revision.id == revision_id,
                Revision.user_id == user_id
            )
            .first()
        )

        if not revision:
            raise ValueError(
                "Revision not found."
            )

        if revision.status == "completed":
            raise ValueError(
                "This revision is already completed."
            )

        # --------------------------------------------------------
        # Validate recall score
        # --------------------------------------------------------

        recall_score = max(
            0.0,
            min(100.0, recall_score)
        )

        revision.recall_score = recall_score
        revision.completed_at = datetime.utcnow()
        revision.status = "completed"

        db.commit()
        db.refresh(revision)

        # --------------------------------------------------------
        # Get mastery
        # --------------------------------------------------------

        mastery = (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id,
                Mastery.topic_id == revision.topic_id
            )
            .first()
        )

        if mastery:

            # ----------------------------------------------------
            # Update forgetting risk after successful revision
            # ----------------------------------------------------

            mastery.forgetting_risk = 0.0
            mastery.updated_at = datetime.utcnow()

            db.commit()

            # ----------------------------------------------------
            # Schedule next revision based on recall
            # ----------------------------------------------------

            next_revision = (
                RevisionService.schedule_revision(
                    db=db,
                    user_id=user_id,
                    topic_id=revision.topic_id,
                    mastery_score=mastery.mastery_score,
                    recall_score=recall_score
                )
            )

        else:

            next_revision = None

        return {
            "revision_id": revision.id,
            "topic_id": revision.topic_id,
            "recall_score": recall_score,
            "completed_at": revision.completed_at,
            "next_revision_id": (
                next_revision.id
                if next_revision
                else None
            ),
            "next_revision_at": (
                next_revision.scheduled_at
                if next_revision
                else None
            )
        }

    # ============================================================
    # GET DUE REVISIONS
    # ============================================================

    @staticmethod
    def get_due_revisions(
        db: Session,
        user_id: int
    ):

        now = datetime.utcnow()

        revisions = (
            db.query(Revision)
            .filter(
                Revision.user_id == user_id,
                Revision.status == "scheduled",
                Revision.scheduled_at <= now
            )
            .order_by(
                Revision.scheduled_at.asc()
            )
            .all()
        )

        return revisions

    # ============================================================
    # GET UPCOMING REVISIONS
    # ============================================================

    @staticmethod
    def get_upcoming_revisions(
        db: Session,
        user_id: int,
        days: int = 7
    ):

        now = datetime.utcnow()

        end_date = (
            now + timedelta(days=days)
        )

        revisions = (
            db.query(Revision)
            .filter(
                Revision.user_id == user_id,
                Revision.status == "scheduled",
                Revision.scheduled_at > now,
                Revision.scheduled_at <= end_date
            )
            .order_by(
                Revision.scheduled_at.asc()
            )
            .all()
        )

        return revisions

    # ============================================================
    # AUTO SCHEDULE WEAK TOPICS
    # ============================================================

    @staticmethod
    def auto_schedule_for_user(
        db: Session,
        user_id: int
    ):

        masteries = (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id
            )
            .all()
        )

        scheduled = []

        for mastery in masteries:

            # ----------------------------------------------------
            # Weak/developing topics should receive revision.
            # ----------------------------------------------------

            if mastery.mastery_score < 85:

                revision = (
                    RevisionService.schedule_revision(
                        db=db,
                        user_id=user_id,
                        topic_id=mastery.topic_id,
                        mastery_score=mastery.mastery_score
                    )
                )

                scheduled.append(revision)

        return scheduled

    # ============================================================
    # REVISION DASHBOARD
    # ============================================================

    @staticmethod
    def get_revision_dashboard(
        db: Session,
        user_id: int
    ):

        now = datetime.utcnow()

        revisions = (
            db.query(
                Revision,
                Topic,
                Mastery
            )
            .join(
                Topic,
                Revision.topic_id == Topic.id
            )
            .outerjoin(
                Mastery,
                (
                    (Mastery.topic_id == Revision.topic_id)
                    &
                    (Mastery.user_id == user_id)
                )
            )
            .filter(
                Revision.user_id == user_id,
                Revision.status == "scheduled"
            )
            .all()
        )

        results = []

        for revision, topic, mastery in revisions:

            mastery_score = (
                mastery.mastery_score
                if mastery
                else 0.0
            )

            forgetting_risk = (
                mastery.forgetting_risk
                if mastery
                else 0.0
            )

            mistake_count = (
                db.query(Mistake)
                .filter(
                    Mistake.user_id == user_id,
                    Mistake.topic_id == topic.id
                )
                .count()
            )

            days_since_revision = max(
                0,
                (
                    now - revision.created_at
                ).total_seconds() / 86400
            )

            priority = (
                RevisionService.calculate_priority(
                    mastery_score=mastery_score,
                    forgetting_risk=forgetting_risk,
                    mistake_count=mistake_count,
                    days_since_revision=days_since_revision
                )
            )

            results.append({
                "revision_id": revision.id,
                "topic_id": topic.id,
                "topic": topic.name,
                "scheduled_at": revision.scheduled_at,
                "mastery_score": round(
                    mastery_score,
                    2
                ),
                "forgetting_risk": round(
                    forgetting_risk,
                    2
                ),
                "mistake_count": mistake_count,
                "priority_score": priority,
                "status": revision.status
            })

        # --------------------------------------------------------
        # Highest priority first
        # --------------------------------------------------------

        results.sort(
            key=lambda item: item["priority_score"],
            reverse=True
        )

        return results