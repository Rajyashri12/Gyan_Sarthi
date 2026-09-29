from sqlalchemy.orm import Session

from app.models.attempt import Attempt
from app.models.mistake import Mistake
from app.models.mastery import Mastery
from app.models.question import Question
from app.models.subject import Subject
from app.models.topic import Topic


class AdaptiveQuestionService:

    # =====================================================
    # BASIC HELPERS
    # =====================================================

    @staticmethod
    def get_recent_question_ids(
        db: Session,
        user_id: int,
        limit: int = 20,
    ):

        attempts = (
            db.query(Attempt.question_id)
            .filter(
                Attempt.user_id == user_id
            )
            .order_by(
                Attempt.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return {
            question_id
            for (question_id,) in attempts
        }

    @staticmethod
    def get_mistake_question_ids(
        db: Session,
        user_id: int,
        topic_id: int | None = None,
    ):

        query = (
            db.query(Mistake.question_id)
            .filter(
                Mistake.user_id == user_id
            )
        )

        if topic_id:

            query = query.filter(
                Mistake.topic_id == topic_id
            )

        rows = query.all()

        return {
            question_id
            for (question_id,) in rows
        }

    @staticmethod
    def get_mastery(
        db: Session,
        user_id: int,
        topic_id: int,
    ):

        return (
            db.query(Mastery)
            .filter(
                Mastery.user_id == user_id,
                Mastery.topic_id == topic_id,
            )
            .first()
        )

    # =====================================================
    # DIFFICULTY PROFILE
    # =====================================================

    @staticmethod
    def get_difficulty_profile(
        mastery_score: float,
        limit: int,
    ):

        if mastery_score < 40:

            easy = round(limit * 0.60)
            medium = round(limit * 0.30)

        elif mastery_score < 70:

            easy = round(limit * 0.20)
            medium = round(limit * 0.60)

        else:

            easy = round(limit * 0.10)
            medium = round(limit * 0.40)

        hard = limit - easy - medium

        return {
            "easy": easy,
            "medium": medium,
            "hard": hard,
        }

    # =====================================================
    # QUESTION SCORING
    # =====================================================

    @staticmethod
    def score_question(
        question: Question,
        mastery_score: float,
        mistake_question_ids: set[int],
        recent_question_ids: set[int],
    ) -> float:

        score = 0.0

        # -------------------------------------------------
        # Difficulty fit
        # -------------------------------------------------

        if mastery_score < 40:

            if question.difficulty == "easy":
                score += 50

            elif question.difficulty == "medium":
                score += 25

            else:
                score += 5

        elif mastery_score < 70:

            if question.difficulty == "medium":
                score += 50

            elif question.difficulty == "easy":
                score += 25

            else:
                score += 15

        else:

            if question.difficulty == "hard":
                score += 50

            elif question.difficulty == "medium":
                score += 35

            else:
                score += 10

        # -------------------------------------------------
        # Previous mistake
        # -------------------------------------------------

        if question.id in mistake_question_ids:
            score += 25

        # -------------------------------------------------
        # PYQ
        # -------------------------------------------------

        if question.is_pyq:
            score += 15

        # -------------------------------------------------
        # Recent question penalty
        # -------------------------------------------------

        if question.id in recent_question_ids:
            score -= 100

        return score

    # =====================================================
    # GET CANDIDATES
    # =====================================================

    @staticmethod
    def get_candidates(
        db: Session,
        exam_id: int,
        subject_code: str | None = None,
        topic_id: int | None = None,
    ):

        query = (
            db.query(Question)
            .filter(
                Question.exam_id == exam_id
            )
        )

        if subject_code:

            query = (
                query
                .join(
                    Subject,
                    Subject.id == Question.subject_id,
                )
                .filter(
                    Subject.code == subject_code
                )
            )

        if topic_id:

            query = query.filter(
                Question.topic_id == topic_id
            )

        return query.all()

    # =====================================================
    # GET QUESTION MASTERY
    # =====================================================

    @staticmethod
    def get_question_mastery(
        db: Session,
        user_id: int,
        question: Question,
    ):

        mastery = (
            AdaptiveQuestionService
            .get_mastery(
                db=db,
                user_id=user_id,
                topic_id=question.topic_id,
            )
        )

        if mastery:
            return mastery.mastery_score

        return 0.0

    # =====================================================
    # DIVERSITY SELECTION
    # =====================================================

    @staticmethod
    def select_diverse_questions(
        scored_questions,
        limit: int,
    ):

        selected = []

        used_topics = set()

        used_questions = set()

        # -------------------------------------------------
        # PASS 1
        # Prioritize different topics
        # -------------------------------------------------

        for score, question in scored_questions:

            if len(selected) >= limit:
                break

            if question.id in used_questions:
                continue

            if question.topic_id in used_topics:
                continue

            selected.append(question)

            used_questions.add(
                question.id
            )

            used_topics.add(
                question.topic_id
            )

        # -------------------------------------------------
        # PASS 2
        # Fill remaining slots
        # -------------------------------------------------

        for score, question in scored_questions:

            if len(selected) >= limit:
                break

            if question.id in used_questions:
                continue

            selected.append(question)

            used_questions.add(
                question.id
            )

        return selected

    # =====================================================
    # MAIN ADAPTIVE ENGINE
    # =====================================================

    @staticmethod
    def get_adaptive_questions(
        db: Session,
        user_id: int,
        exam_id: int,
        subject_code: str | None = None,
        topic_id: int | None = None,
        limit: int = 10,
    ):

        candidates = (
            AdaptiveQuestionService
            .get_candidates(
                db=db,
                exam_id=exam_id,
                subject_code=subject_code,
                topic_id=topic_id,
            )
        )

        if not candidates:
            return []

        recent_question_ids = (
            AdaptiveQuestionService
            .get_recent_question_ids(
                db=db,
                user_id=user_id,
            )
        )

        mistake_question_ids = (
            AdaptiveQuestionService
            .get_mistake_question_ids(
                db=db,
                user_id=user_id,
                topic_id=topic_id,
            )
        )

        # -------------------------------------------------
        # Score every candidate
        # -------------------------------------------------

        scored_questions = []

        for question in candidates:

            mastery_score = (
                AdaptiveQuestionService
                .get_question_mastery(
                    db=db,
                    user_id=user_id,
                    question=question,
                )
            )

            score = (
                AdaptiveQuestionService
                .score_question(
                    question=question,
                    mastery_score=mastery_score,
                    mistake_question_ids=(
                        mistake_question_ids
                    ),
                    recent_question_ids=(
                        recent_question_ids
                    ),
                )
            )

            scored_questions.append(
                (
                    score,
                    question,
                )
            )

        # -------------------------------------------------
        # Highest score first
        # -------------------------------------------------

        scored_questions.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # -------------------------------------------------
        # Remove recent questions
        # -------------------------------------------------

        fresh_questions = [
            (score, question)
            for score, question
            in scored_questions
            if question.id
            not in recent_question_ids
        ]

        if fresh_questions:

            scored_questions = fresh_questions

        # -------------------------------------------------
        # Determine mastery
        # -------------------------------------------------

        if topic_id:

            mastery = (
                AdaptiveQuestionService
                .get_mastery(
                    db=db,
                    user_id=user_id,
                    topic_id=topic_id,
                )
            )

            mastery_score = (
                mastery.mastery_score
                if mastery
                else 0.0
            )

        else:

            mastery_scores = []

            for question in candidates:

                mastery = (
                    AdaptiveQuestionService
                    .get_mastery(
                        db=db,
                        user_id=user_id,
                        topic_id=question.topic_id,
                    )
                )

                if mastery:
                    mastery_scores.append(
                        mastery.mastery_score
                    )

            mastery_score = (
                sum(mastery_scores)
                / len(mastery_scores)
                if mastery_scores
                else 0.0
            )

        # -------------------------------------------------
        # Difficulty profile
        # -------------------------------------------------

        difficulty_profile = (
            AdaptiveQuestionService
            .get_difficulty_profile(
                mastery_score=mastery_score,
                limit=limit,
            )
        )

        # -------------------------------------------------
        # Select by difficulty
        # -------------------------------------------------

        selected = []

        difficulty_counts = {
            "easy": 0,
            "medium": 0,
            "hard": 0,
        }

        # First pass:
        # respect difficulty targets
        for score, question in scored_questions:

            if len(selected) >= limit:
                break

            difficulty = (
                question.difficulty.lower()
            )

            if difficulty not in difficulty_counts:
                difficulty = "medium"

            target = difficulty_profile[
                difficulty
            ]

            if (
                difficulty_counts[difficulty]
                >= target
            ):
                continue

            selected.append(question)

            difficulty_counts[
                difficulty
            ] += 1

        # -------------------------------------------------
        # Second pass:
        # fill missing questions
        # -------------------------------------------------

        for score, question in scored_questions:

            if len(selected) >= limit:
                break

            if question in selected:
                continue

            selected.append(question)

        # -------------------------------------------------
        # Diversity pass
        # -------------------------------------------------

        scored_selected = []

        for question in selected:

            score = 0

            for candidate_score, candidate_question in (
                scored_questions
            ):

                if candidate_question.id == question.id:

                    score = candidate_score
                    break

            scored_selected.append(
                (
                    score,
                    question,
                )
            )

        diverse = (
            AdaptiveQuestionService
            .select_diverse_questions(
                scored_questions=scored_selected,
                limit=limit,
            )
        )

        return diverse[:limit]