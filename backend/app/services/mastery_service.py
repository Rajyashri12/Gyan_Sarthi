from datetime import datetime

from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.question import Question
from app.models.mastery import Mastery


class MasteryService:

    # ============================================================
    # CLAMP VALUE
    # ============================================================

    @staticmethod
    def clamp(
        value: float,
        minimum: float = 0.0,
        maximum: float = 100.0,
    ) -> float:

        return max(
            minimum,
            min(maximum, value),
        )

    # ============================================================
    # NORMALIZE CONFIDENCE
    # ============================================================

    @staticmethod
    def normalize_confidence(
        confidence: float | None,
    ) -> float:
        """
        Convert confidence into a 0.0 - 1.0 scale.

        Supported formats:

        0.0 - 1.0
        Example:
            0.8 -> 0.8

        1 - 5
        Example:
            3 -> 0.6
            4 -> 0.8
            5 -> 1.0
        """

        if confidence is None:
            return 0.0

        try:
            confidence = float(confidence)

        except (TypeError, ValueError):

            return 0.0

        # --------------------------------------------
        # Already normalized: 0.0 - 1.0
        # --------------------------------------------

        if 0.0 <= confidence <= 1.0:

            return confidence

        # --------------------------------------------
        # 1 - 5 confidence scale
        # --------------------------------------------

        if 1.0 < confidence <= 5.0:

            return confidence / 5.0

        # --------------------------------------------
        # Invalid value
        # --------------------------------------------

        return 0.0

    # ============================================================
    # CALCULATE TOPIC MASTERY
    # ============================================================

    @staticmethod
    def calculate_topic_mastery(
        db: Session,
        user_id: int,
        topic_id: int,
    ):

        # ========================================================
        # GET ATTEMPTS
        # ========================================================

        attempts = (
            db.query(Attempt)
            .join(
                Question,
                Attempt.question_id == Question.id,
            )
            .filter(
                Attempt.user_id == user_id,
                Question.topic_id == topic_id,
            )
            .order_by(
                Attempt.created_at.desc()
            )
            .all()
        )

        # ========================================================
        # NO ATTEMPTS
        # ========================================================

        if not attempts:

            return None

        total_attempts = len(attempts)

        # ========================================================
        # ACCURACY
        # ========================================================

        correct_attempts = sum(
            1
            for attempt in attempts
            if attempt.is_correct
        )

        accuracy = (
            correct_attempts
            / total_attempts
        )

        accuracy = max(
            0.0,
            min(1.0, accuracy),
        )

        # ========================================================
        # AVERAGE TIME
        # ========================================================

        time_values = [
            float(attempt.time_taken_seconds or 0)
            for attempt in attempts
            if attempt.time_taken_seconds is not None
        ]

        if time_values:

            average_time = (
                sum(time_values)
                / len(time_values)
            )

        else:

            average_time = 0.0

        # ========================================================
        # CONFIDENCE
        # ========================================================

        confidence_values = []

        for attempt in attempts:

            if attempt.confidence is None:
                continue

            normalized_confidence = (
                MasteryService.normalize_confidence(
                    attempt.confidence
                )
            )

            confidence_values.append(
                normalized_confidence
            )

        if confidence_values:

            confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )

        else:

            confidence = 0.0

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        # ========================================================
        # RECENT PERFORMANCE
        # ========================================================

        recent_attempts = attempts[:5]

        recent_correct = sum(
            1
            for attempt in recent_attempts
            if attempt.is_correct
        )

        recent_accuracy = (
            recent_correct
            / len(recent_attempts)
        )

        recent_accuracy = max(
            0.0,
            min(1.0, recent_accuracy),
        )

        # ========================================================
        # SPEED SCORE
        # ========================================================

        if average_time <= 0:

            speed_score = 0.0

        else:

            speed_score = (
                60.0
                / max(
                    average_time,
                    60.0,
                )
            )

        speed_score = max(
            0.0,
            min(1.0, speed_score),
        )

        # ========================================================
        # MASTERY CALCULATION
        # ========================================================

        mastery_normalized = (
            (accuracy * 0.50)
            +
            (confidence * 0.20)
            +
            (recent_accuracy * 0.20)
            +
            (speed_score * 0.10)
        )

        # ========================================================
        # SAFETY CLAMP
        # ========================================================

        mastery_normalized = max(
            0.0,
            min(1.0, mastery_normalized),
        )

        # Convert 0-1 → 0-100

        mastery_score = (
            mastery_normalized * 100.0
        )

        # Final safety clamp

        mastery_score = MasteryService.clamp(
            mastery_score,
            0.0,
            100.0,
        )

        mastery_score = round(
            mastery_score,
            2,
        )

        # ========================================================
        # FORGETTING RISK
        # ========================================================

        latest_attempt = attempts[0]

        if latest_attempt.created_at:

            days_since_attempt = max(
                0,
                (
                    datetime.utcnow()
                    - latest_attempt.created_at
                ).days,
            )

        else:

            days_since_attempt = 0

        forgetting_risk = min(
            1.0,
            max(
                0.0,
                days_since_attempt / 30.0,
            ),
        )

        # ========================================================
        # GET EXISTING MASTERY
        # ========================================================

        mastery = (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id,
                Mastery.topic_id == topic_id,
            )
            .first()
        )

        # ========================================================
        # CREATE IF NOT EXISTS
        # ========================================================

        if not mastery:

            mastery = Mastery(
                user_id=user_id,
                topic_id=topic_id,
            )

            db.add(mastery)

        # ========================================================
        # UPDATE MASTERY
        # ========================================================

        mastery.mastery_score = (
            mastery_score
        )

        mastery.accuracy = round(
            accuracy * 100.0,
            2,
        )

        mastery.average_time_seconds = round(
            average_time,
            2,
        )

        mastery.attempts_count = (
            total_attempts
        )

        mastery.confidence_score = round(
            confidence * 100.0,
            2,
        )

        mastery.forgetting_risk = round(
            forgetting_risk * 100.0,
            2,
        )

        mastery.updated_at = datetime.utcnow()

        # ========================================================
        # DEBUG INFORMATION
        # ========================================================

        print(
            "\n================ MASTERY DEBUG ================"
        )

        print(
            f"User ID             : {user_id}"
        )

        print(
            f"Topic ID            : {topic_id}"
        )

        print(
            f"Total Attempts      : {total_attempts}"
        )

        print(
            f"Correct Attempts    : {correct_attempts}"
        )

        print(
            f"Accuracy            : {accuracy * 100:.2f}%"
        )

        print(
            f"Confidence Values   : {confidence_values}"
        )

        print(
            f"Confidence          : {confidence * 100:.2f}%"
        )

        print(
            f"Recent Accuracy     : {recent_accuracy * 100:.2f}%"
        )

        print(
            f"Average Time        : {average_time:.2f}s"
        )

        print(
            f"Speed Score         : {speed_score * 100:.2f}%"
        )

        print(
            f"Mastery Score       : {mastery_score:.2f}%"
        )

        print(
            f"Forgetting Risk     : {forgetting_risk * 100:.2f}%"
        )

        print(
            "===============================================\n"
        )

        # ========================================================
        # SAVE
        # ========================================================

        db.commit()

        db.refresh(mastery)

        return mastery

    # ============================================================
    # CLASSIFY MASTERY
    # ============================================================

    @staticmethod
    def classify_mastery(
        mastery_score: float,
    ) -> str:

        mastery_score = MasteryService.clamp(
            mastery_score,
            0.0,
            100.0,
        )

        if mastery_score < 40:

            return "WEAK"

        if mastery_score < 70:

            return "DEVELOPING"

        if mastery_score < 85:

            return "STRONG"

        return "MASTERED"