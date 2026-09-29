from datetime import datetime

from sqlalchemy.orm import Session

from app.models.mastery import Mastery
from app.models.mistake import Mistake
from app.models.topic import Topic
from app.models.subject import Subject
from app.models.question import Question
from app.models.attempt import Attempt


class AdaptiveService:

    # ============================================================
    # RECENCY SCORE
    # ============================================================

    @staticmethod
    def calculate_recency_score(
        forgetting_risk: float
    ) -> float:
        """
        Higher recency means the student has interacted with
        the topic more recently.

        forgetting_risk is expected between 0 and 100.
        """

        forgetting_risk = max(
            0.0,
            min(100.0, forgetting_risk)
        )

        return round(
            100.0 - forgetting_risk,
            2
        )

    # ============================================================
    # MISTAKE SCORE
    # ============================================================

    @staticmethod
    def calculate_mistake_score(
        mistake_count: int
    ) -> float:
        """
        Convert repeated mistakes into a 0-100 priority signal.
        Five or more mistakes are capped at 100.
        """

        if mistake_count <= 0:
            return 0.0

        score = min(
            mistake_count / 5.0,
            1.0
        )

        return round(
            score * 100,
            2
        )

    # ============================================================
    # RECENT PERFORMANCE
    # ============================================================

    @staticmethod
    def calculate_recent_performance(
        db: Session,
        user_id: int,
        topic_id: int,
        limit: int = 5
    ) -> float:
        """
        Calculate recent accuracy for a topic.

        Returns:
            0-100
        """

        attempts = (
            db.query(Attempt)
            .join(
                Question,
                Attempt.question_id == Question.id
            )
            .filter(
                Attempt.user_id == user_id,
                Question.topic_id == topic_id
            )
            .order_by(
                Attempt.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        if not attempts:
            return 0.0

        correct = sum(
            1
            for attempt in attempts
            if attempt.is_correct
        )

        accuracy = (
            correct / len(attempts)
        ) * 100

        return round(
            accuracy,
            2
        )

    # ============================================================
    # PERFORMANCE RISK
    # ============================================================

    @staticmethod
    def calculate_performance_risk(
        recent_performance: float
    ) -> float:
        """
        Convert recent performance into risk.

        Low recent performance = high risk.
        """

        recent_performance = max(
            0.0,
            min(100.0, recent_performance)
        )

        return round(
            100.0 - recent_performance,
            2
        )

    # ============================================================
    # DETERMINE ACTION
    # ============================================================

    @staticmethod
    def determine_action(
        mastery_score: float,
        forgetting_risk: float,
        mistake_count: int,
        recent_performance: float
    ) -> str:
        """
        Decide what the student should do next.
        """

        # --------------------------------------------------------
        # Severe weakness
        # --------------------------------------------------------

        if mastery_score < 40:

            return "LEARN"

        # --------------------------------------------------------
        # Repeated mistakes
        # --------------------------------------------------------

        if mistake_count >= 3:

            if mastery_score < 60:
                return "LEARN"

            return "TARGETED_PRACTICE"

        # --------------------------------------------------------
        # Recent performance is very poor
        # --------------------------------------------------------

        if recent_performance > 0 and recent_performance < 40:

            if mastery_score < 60:
                return "LEARN"

            return "TARGETED_PRACTICE"

        # --------------------------------------------------------
        # High forgetting risk
        # --------------------------------------------------------

        if forgetting_risk >= 70:

            return "REVISE"

        # --------------------------------------------------------
        # Developing topic
        # --------------------------------------------------------

        if mastery_score < 70:

            return "PRACTICE"

        # --------------------------------------------------------
        # Strong topic but needs maintenance
        # --------------------------------------------------------

        if mastery_score < 85:

            return "REVISE"

        # --------------------------------------------------------
        # High mastery
        # --------------------------------------------------------

        return "MOCK_TEST"

    # ============================================================
    # PRIORITY SCORE
    # ============================================================

    @staticmethod
    def calculate_priority(
        mastery_score: float,
        forgetting_risk: float,
        mistake_score: float,
        recent_performance: float
    ) -> float:
        """
        Calculate adaptive priority.

        Higher score = topic should be addressed sooner.

        Weights:
            Weakness          = 35%
            Forgetting        = 25%
            Mistakes          = 20%
            Recent performance= 20%
        """

        mastery_score = max(
            0.0,
            min(100.0, mastery_score)
        )

        forgetting_risk = max(
            0.0,
            min(100.0, forgetting_risk)
        )

        mistake_score = max(
            0.0,
            min(100.0, mistake_score)
        )

        recent_performance = max(
            0.0,
            min(100.0, recent_performance)
        )

        weakness_score = (
            100.0 - mastery_score
        )

        performance_risk = (
            100.0 - recent_performance
        )

        priority = (
            weakness_score * 0.35
            + forgetting_risk * 0.25
            + mistake_score * 0.20
            + performance_risk * 0.20
        )

        return round(
            priority,
            2
        )

    # ============================================================
    # QUESTION COUNT
    # ============================================================

    @staticmethod
    def calculate_question_count(
        mastery_score: float,
        priority_score: float,
        mistake_count: int
    ) -> int:
        """
        Decide how many practice questions should be recommended.
        """

        # --------------------------------------------------------
        # Very weak
        # --------------------------------------------------------

        if mastery_score < 40:

            count = 15

        # --------------------------------------------------------
        # Developing
        # --------------------------------------------------------

        elif mastery_score < 60:

            count = 12

        elif mastery_score < 70:

            count = 10

        # --------------------------------------------------------
        # Strong
        # --------------------------------------------------------

        elif mastery_score < 85:

            count = 7

        else:

            count = 5

        # --------------------------------------------------------
        # Increase practice for repeated mistakes
        # --------------------------------------------------------

        if mistake_count >= 3:

            count += 3

        elif mistake_count >= 2:

            count += 2

        # --------------------------------------------------------
        # Priority adjustment
        # --------------------------------------------------------

        if priority_score >= 80:

            count += 2

        # --------------------------------------------------------
        # Keep reasonable bounds
        # --------------------------------------------------------

        return max(
            5,
            min(20, count)
        )

    # ============================================================
    # ESTIMATED MINUTES
    # ============================================================

    @staticmethod
    def calculate_estimated_minutes(
        question_count: int,
        mastery_score: float
    ) -> int:
        """
        Estimate practice duration.

        Weak topics are given slightly more time per question.
        """

        if mastery_score < 40:

            seconds_per_question = 120

        elif mastery_score < 70:

            seconds_per_question = 90

        else:

            seconds_per_question = 60

        total_seconds = (
            question_count
            * seconds_per_question
        )

        return max(
            5,
            round(total_seconds / 60)
        )

    # ============================================================
    # GET TOPIC PLAN
    # ============================================================

    @staticmethod
    def get_topic_plan(
        db: Session,
        user_id: int,
        topic: Topic
    ):
        """
        Generate adaptive recommendation for one topic.
        """

        # --------------------------------------------------------
        # Get mastery
        # --------------------------------------------------------

        mastery = (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id,
                Mastery.topic_id == topic.id
            )
            .first()
        )

        # --------------------------------------------------------
        # No mastery = not assessed
        # --------------------------------------------------------

        if mastery is None:

            mastery_score = 0.0
            forgetting_risk = 0.0

        else:

            mastery_score = mastery.mastery_score
            forgetting_risk = mastery.forgetting_risk

        # --------------------------------------------------------
        # Mistakes
        # --------------------------------------------------------

        mistake_count = (
            db.query(Mistake)
            .filter(
                Mistake.user_id == user_id,
                Mistake.topic_id == topic.id
            )
            .count()
        )

        mistake_score = (
            AdaptiveService.calculate_mistake_score(
                mistake_count
            )
        )

        # --------------------------------------------------------
        # Recency
        # --------------------------------------------------------

        recency_score = (
            AdaptiveService.calculate_recency_score(
                forgetting_risk
            )
        )

        # --------------------------------------------------------
        # Recent performance
        # --------------------------------------------------------

        recent_performance = (
            AdaptiveService.calculate_recent_performance(
                db=db,
                user_id=user_id,
                topic_id=topic.id
            )
        )

        # --------------------------------------------------------
        # Priority
        # --------------------------------------------------------

        priority_score = (
            AdaptiveService.calculate_priority(
                mastery_score=mastery_score,
                forgetting_risk=forgetting_risk,
                mistake_score=mistake_score,
                recent_performance=recent_performance
            )
        )

        # --------------------------------------------------------
        # Action
        # --------------------------------------------------------

        action = (
            AdaptiveService.determine_action(
                mastery_score=mastery_score,
                forgetting_risk=forgetting_risk,
                mistake_count=mistake_count,
                recent_performance=recent_performance
            )
        )

        # --------------------------------------------------------
        # Question count
        # --------------------------------------------------------

        question_count = (
            AdaptiveService.calculate_question_count(
                mastery_score=mastery_score,
                priority_score=priority_score,
                mistake_count=mistake_count
            )
        )

        # --------------------------------------------------------
        # Estimated time
        # --------------------------------------------------------

        estimated_minutes = (
            AdaptiveService.calculate_estimated_minutes(
                question_count=question_count,
                mastery_score=mastery_score
            )
        )

        return {
            "topic_id": topic.id,
            "topic": topic.name,
            "mastery_score": round(
                mastery_score,
                2
            ),
            "forgetting_risk": round(
                forgetting_risk,
                2
            ),
            "mistake_score": round(
                mistake_score,
                2
            ),
            "recency_score": round(
                recency_score,
                2
            ),
            "recent_performance": round(
                recent_performance,
                2
            ),
            "priority_score": round(
                priority_score,
                2
            ),
            "action": action,
            "recommended_questions": question_count,
            "estimated_minutes": estimated_minutes,
            "mistake_count": mistake_count,
        }

    # ============================================================
    # GET ADAPTIVE PLAN
    # ============================================================

    @staticmethod
    def get_adaptive_plan(
        db: Session,
        user_id: int,
        exam_id: int
    ):
        """
        Generate an adaptive plan for every topic in the exam.
        """

        topics = (
            db.query(Topic)
            .join(
                Subject,
                Topic.subject_id == Subject.id
            )
            .filter(
                Subject.exam_id == exam_id,
                Topic.parent_topic_id.is_(None)
            )
            .order_by(
                Topic.id.asc()
            )
            .all()
        )

        plans = []

        for topic in topics:

            plan = AdaptiveService.get_topic_plan(
                db=db,
                user_id=user_id,
                topic=topic
            )

            plans.append(plan)

        # --------------------------------------------------------
        # Highest priority first
        # --------------------------------------------------------

        plans.sort(
            key=lambda item: item["priority_score"],
            reverse=True
        )

        return plans

    # ============================================================
    # TODAY'S PLAN
    # ============================================================

    @staticmethod
    def get_today_plan(
        db: Session,
        user_id: int,
        exam_id: int,
        limit: int = 5
    ):
        """
        Return the highest-priority topics for today.
        """

        plans = AdaptiveService.get_adaptive_plan(
            db=db,
            user_id=user_id,
            exam_id=exam_id
        )

        return plans[:limit]