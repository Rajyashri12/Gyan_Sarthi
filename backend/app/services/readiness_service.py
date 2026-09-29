from datetime import datetime

from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.exam_session import ExamSession
from app.models.mastery import Mastery
from app.models.question import Question
from app.models.readiness import Readiness
from app.models.topic import Topic


class ReadinessService:

    @staticmethod
    def clamp(value: float) -> float:
        return max(0.0, min(100.0, value))

    @staticmethod
    def calculate_mastery_score(
        db: Session,
        user_id: int,
        exam_id: int,
    ) -> float:

        masteries = (
            db.query(Mastery)
            .join(
                Topic,
                Topic.id == Mastery.topic_id,
            )
            .join(
                Question,
                Question.topic_id == Topic.id,
            )
            .filter(
                Mastery.user_id == user_id,
                Question.exam_id == exam_id,
            )
            .distinct()
            .all()
        )

        if not masteries:
            return 0.0

        # Avoid counting the same topic multiple times
        unique_mastery = {}

        for mastery in masteries:
            unique_mastery[mastery.topic_id] = mastery

        scores = [
            mastery.mastery_score
            for mastery in unique_mastery.values()
        ]

        return round(
            sum(scores) / len(scores),
            2,
        )

    @staticmethod
    def calculate_exam_performance(
        db: Session,
        user_id: int,
        exam_id: int,
    ) -> float:

        sessions = (
            db.query(ExamSession)
            .filter(
                ExamSession.user_id == user_id,
                ExamSession.exam_id == exam_id,
                ExamSession.status == "submitted",
            )
            .order_by(
                ExamSession.submitted_at.desc()
            )
            .limit(5)
            .all()
        )

        if not sessions:
            return 0.0

        scores = []

        for session in sessions:

            if session.total_marks <= 0:
                continue

            percentage = (
                session.score /
                session.total_marks
            ) * 100

            scores.append(
                ReadinessService.clamp(
                    percentage
                )
            )

        if not scores:
            return 0.0

        return round(
            sum(scores) / len(scores),
            2,
        )

    @staticmethod
    def calculate_accuracy(
        db: Session,
        user_id: int,
        exam_id: int,
    ) -> float:

        attempts = (
            db.query(Attempt)
            .join(
                Question,
                Question.id == Attempt.question_id,
            )
            .filter(
                Attempt.user_id == user_id,
                Question.exam_id == exam_id,
            )
            .all()
        )

        if not attempts:
            return 0.0

        correct = sum(
            1
            for attempt in attempts
            if attempt.is_correct
        )

        return round(
            (correct / len(attempts)) * 100,
            2,
        )

    @staticmethod
    def calculate_speed(
        db: Session,
        user_id: int,
        exam_id: int,
    ) -> float:

        attempts = (
            db.query(Attempt)
            .join(
                Question,
                Question.id == Attempt.question_id,
            )
            .filter(
                Attempt.user_id == user_id,
                Question.exam_id == exam_id,
                Attempt.time_taken_seconds > 0,
            )
            .all()
        )

        if not attempts:
            return 0.0

        average_time = (
            sum(
                attempt.time_taken_seconds
                for attempt in attempts
            )
            / len(attempts)
        )

        # MVP benchmark:
        # 60 seconds/question = 100 speed score
        speed = (
            60 / max(average_time, 60)
        ) * 100

        return round(
            ReadinessService.clamp(speed),
            2,
        )

    @staticmethod
    def calculate_consistency(
        db: Session,
        user_id: int,
        exam_id: int,
    ) -> float:

        sessions = (
            db.query(ExamSession)
            .filter(
                ExamSession.user_id == user_id,
                ExamSession.exam_id == exam_id,
                ExamSession.status == "submitted",
            )
            .order_by(
                ExamSession.submitted_at.desc()
            )
            .limit(5)
            .all()
        )

        if len(sessions) < 2:
            return 50.0

        scores = []

        for session in sessions:

            if session.total_marks <= 0:
                continue

            percentage = (
                session.score /
                session.total_marks
            ) * 100

            scores.append(
                ReadinessService.clamp(
                    percentage
                )
            )

        if len(scores) < 2:
            return 50.0

        mean = sum(scores) / len(scores)

        variance = sum(
            (score - mean) ** 2
            for score in scores
        ) / len(scores)

        standard_deviation = variance ** 0.5

        consistency = max(
            0.0,
            100.0 - standard_deviation * 2,
        )

        return round(
            ReadinessService.clamp(
                consistency
            ),
            2,
        )

    @staticmethod
    def calculate_readiness(
        db: Session,
        user_id: int,
        exam_id: int,
    ):

        mastery = (
            ReadinessService.calculate_mastery_score(
                db,
                user_id,
                exam_id,
            )
        )

        exam_performance = (
            ReadinessService.calculate_exam_performance(
                db,
                user_id,
                exam_id,
            )
        )

        accuracy = (
            ReadinessService.calculate_accuracy(
                db,
                user_id,
                exam_id,
            )
        )

        speed = (
            ReadinessService.calculate_speed(
                db,
                user_id,
                exam_id,
            )
        )

        consistency = (
            ReadinessService.calculate_consistency(
                db,
                user_id,
                exam_id,
            )
        )

        readiness_score = (
            mastery * 0.40
            + exam_performance * 0.30
            + accuracy * 0.10
            + speed * 0.10
            + consistency * 0.10
        )

        readiness_score = round(
            ReadinessService.clamp(
                readiness_score
            ),
            2,
        )

        existing = (
            db.query(Readiness)
            .filter(
                Readiness.user_id == user_id,
                Readiness.exam_id == exam_id,
            )
            .first()
        )

        if existing:

            existing.readiness_score = readiness_score
            existing.mastery_score = mastery
            existing.exam_performance_score = exam_performance
            existing.accuracy_score = accuracy
            existing.speed_score = speed
            existing.consistency_score = consistency

            readiness = existing

        else:

            readiness = Readiness(
                user_id=user_id,
                exam_id=exam_id,
                readiness_score=readiness_score,
                mastery_score=mastery,
                exam_performance_score=exam_performance,
                accuracy_score=accuracy,
                speed_score=speed,
                consistency_score=consistency,
            )

            db.add(readiness)

        db.commit()
        db.refresh(readiness)

        return readiness

    @staticmethod
    def get_readiness_level(
        score: float,
    ) -> str:

        if score < 40:
            return "NEEDS_IMPROVEMENT"

        if score < 60:
            return "DEVELOPING"

        if score < 75:
            return "ON_TRACK"

        if score < 90:
            return "STRONG"

        return "HIGH_READINESS"

    @staticmethod
    def get_topic_analysis(
        db: Session,
        user_id: int,
        exam_id: int,
    ):

        rows = (
            db.query(
                Mastery.topic_id,
                Topic.name,
                Mastery.mastery_score,
            )
            .join(
                Topic,
                Topic.id == Mastery.topic_id,
            )
            .join(
                Question,
                Question.topic_id == Topic.id,
            )
            .filter(
                Mastery.user_id == user_id,
                Question.exam_id == exam_id,
            )
            .distinct()
            .all()
        )

        topics = {}

        for row in rows:

            topics[row.topic_id] = {
                "topic_id": row.topic_id,
                "topic": row.name,
                "mastery_score": round(
                    row.mastery_score,
                    2,
                ),
            }

        result = []

        for item in topics.values():

            score = item["mastery_score"]

            if score < 40:
                status = "WEAK"
            elif score < 70:
                status = "DEVELOPING"
            elif score < 85:
                status = "STRONG"
            else:
                status = "MASTERED"

            item["status"] = status

            result.append(item)

        return result