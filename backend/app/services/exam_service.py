from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.exam_answer import ExamAnswer
from app.models.exam_session import ExamSession
from app.models.exam_session_question import ExamSessionQuestion
from app.models.question import Question
from app.models.topic import Topic
from app.models.attempt import Attempt

from app.services.mastery_service import MasteryService


class ExamService:

    # =========================================================
    # START EXAM
    # =========================================================

    @staticmethod
    def start_exam(
        db: Session,
        user_id: int,
        exam_id: int,
        total_questions: int,
        duration_minutes: int,
    ):

        # -----------------------------------------------------
        # CHECK EXAM
        # -----------------------------------------------------

        exam = (
            db.query(Exam)
            .filter(
                Exam.id == exam_id
            )
            .first()
        )

        if not exam:
            raise ValueError(
                "Exam not found."
            )

        # -----------------------------------------------------
        # GET RANDOM QUESTIONS
        # -----------------------------------------------------

        questions = (
            db.query(Question)
            .filter(
                Question.exam_id == exam_id
            )
            .order_by(
                func.random()
            )
            .limit(total_questions)
            .all()
        )

        if len(questions) < total_questions:
            raise ValueError(
                f"Only {len(questions)} questions "
                f"are available for this exam."
            )

        # -----------------------------------------------------
        # CREATE EXAM SESSION
        # -----------------------------------------------------

        session = ExamSession(
            user_id=user_id,
            exam_id=exam_id,
            total_questions=len(questions),
            duration_minutes=duration_minutes,
            started_at=datetime.utcnow(),
            status="in_progress",
        )

        db.add(session)

        # Get session ID
        db.flush()

        # -----------------------------------------------------
        # STORE EXACT QUESTIONS FOR SESSION
        # -----------------------------------------------------

        for question in questions:

            session_question = ExamSessionQuestion(
                session_id=session.id,
                question_id=question.id,
            )

            db.add(session_question)

        db.commit()

        db.refresh(session)

        return session, questions

    # =========================================================
    # SAVE ANSWER
    # =========================================================

    @staticmethod
    def save_answer(
        db: Session,
        user_id: int,
        session_id: int,
        question_id: int,
        selected_answer: str | None,
        time_taken_seconds: int,
    ):

        # -----------------------------------------------------
        # FIND SESSION
        # -----------------------------------------------------

        session = (
            db.query(ExamSession)
            .filter(
                ExamSession.id == session_id,
                ExamSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            raise ValueError(
                "Exam session not found."
            )

        # -----------------------------------------------------
        # CHECK SESSION STATUS
        # -----------------------------------------------------

        if session.status != "in_progress":
            raise ValueError(
                "Exam is already submitted."
            )

        # -----------------------------------------------------
        # CHECK TIMEOUT
        # -----------------------------------------------------

        deadline = (
            session.started_at
            + timedelta(
                minutes=session.duration_minutes
            )
        )

        if datetime.utcnow() > deadline:
            raise ValueError(
                "Exam time has expired."
            )

        # -----------------------------------------------------
        # VERIFY QUESTION BELONGS TO SESSION
        # -----------------------------------------------------

        session_question = (
            db.query(ExamSessionQuestion)
            .filter(
                ExamSessionQuestion.session_id
                == session_id,

                ExamSessionQuestion.question_id
                == question_id,
            )
            .first()
        )

        if not session_question:
            raise ValueError(
                "Question does not belong to this exam session."
            )

        # -----------------------------------------------------
        # GET QUESTION
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # NORMALIZE ANSWER
        # -----------------------------------------------------

        normalized_answer = (
            selected_answer.strip().upper()
            if selected_answer
            else None
        )

        # -----------------------------------------------------
        # CHECK EXISTING ANSWER
        # -----------------------------------------------------

        answer = (
            db.query(ExamAnswer)
            .filter(
                ExamAnswer.session_id
                == session_id,

                ExamAnswer.question_id
                == question_id,
            )
            .first()
        )

        # -----------------------------------------------------
        # UPDATE EXISTING ANSWER
        # -----------------------------------------------------

        if answer:

            answer.selected_answer = (
                normalized_answer
            )

            answer.time_taken_seconds = (
                time_taken_seconds
            )

            # Important:
            # Reset grading because the student may
            # have changed their answer.
            answer.is_correct = False
            answer.marks_awarded = 0.0

        # -----------------------------------------------------
        # CREATE NEW ANSWER
        # -----------------------------------------------------

        else:

            answer = ExamAnswer(
                session_id=session_id,
                question_id=question_id,
                selected_answer=normalized_answer,
                is_correct=False,
                marks_awarded=0.0,
                time_taken_seconds=time_taken_seconds,
            )

            db.add(answer)

        db.commit()

        db.refresh(answer)

        return answer

    # =========================================================
    # SUBMIT EXAM
    # =========================================================

    @staticmethod
    def submit_exam(
        db: Session,
        user_id: int,
        session_id: int,
    ):

        # -----------------------------------------------------
        # FIND SESSION
        # -----------------------------------------------------

        session = (
            db.query(ExamSession)
            .filter(
                ExamSession.id == session_id,
                ExamSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            raise ValueError(
                "Exam session not found."
            )

        # =====================================================
        # GET EXACT QUESTIONS IN THIS SESSION
        # =====================================================

        session_question_rows = (
            db.query(ExamSessionQuestion)
            .filter(
                ExamSessionQuestion.session_id
                == session_id
            )
            .all()
        )

        question_ids = [
            row.question_id
            for row in session_question_rows
        ]

        # -----------------------------------------------------
        # GET QUESTIONS
        # -----------------------------------------------------

        questions = {}

        if question_ids:

            question_rows = (
                db.query(Question)
                .filter(
                    Question.id.in_(
                        question_ids
                    )
                )
                .all()
            )

            questions = {
                question.id: question
                for question in question_rows
            }

        # =====================================================
        # ALREADY SUBMITTED
        # =====================================================

        if session.status == "submitted":

            answers = (
                db.query(ExamAnswer)
                .filter(
                    ExamAnswer.session_id
                    == session_id
                )
                .all()
            )

            # -------------------------------------------------
            # BACKFILL ATTEMPTS
            #
            # This is important for old exams that were
            # submitted before Attempt creation was implemented.
            # -------------------------------------------------

            ExamService._create_attempts(
                db=db,
                user_id=user_id,
                session_id=session_id,
                answers=answers,
            )

            # -------------------------------------------------
            # RECALCULATE MASTERY
            # -------------------------------------------------

            ExamService._update_mastery(
                db=db,
                user_id=user_id,
                questions=questions,
            )

            # -------------------------------------------------
            # COUNTS
            # -------------------------------------------------

            attempted = sum(
                1
                for answer in answers
                if answer.selected_answer
            )

            correct = sum(
                1
                for answer in answers
                if answer.is_correct
            )

            incorrect = sum(
                1
                for answer in answers
                if answer.selected_answer
                and not answer.is_correct
            )

            unanswered = (
                session.total_questions
                - attempted
            )

            time_used = sum(
                answer.time_taken_seconds or 0
                for answer in answers
            )

            return {
                "session": session,
                "answers": answers,
                "attempted": attempted,
                "correct": correct,
                "incorrect": incorrect,
                "unanswered": unanswered,
                "time_used": time_used,
            }

        # =====================================================
        # GET ANSWERS
        # =====================================================

        answers = (
            db.query(ExamAnswer)
            .filter(
                ExamAnswer.session_id
                == session_id
            )
            .all()
        )

        answer_map = {
            answer.question_id: answer
            for answer in answers
        }

        # =====================================================
        # INITIAL VALUES
        # =====================================================

        total_marks = 0.0
        score = 0.0
        correct = 0

        # =====================================================
        # GRADE EVERY QUESTION
        # =====================================================

        for question_id in question_ids:

            question = questions.get(
                question_id
            )

            if not question:
                continue

            # -------------------------------------------------
            # TOTAL POSSIBLE MARKS
            # -------------------------------------------------

            total_marks += (
                question.marks or 0.0
            )

            answer = answer_map.get(
                question_id
            )

            # -------------------------------------------------
            # UNANSWERED QUESTION
            # -------------------------------------------------

            if not answer:

                answer = ExamAnswer(
                    session_id=session_id,
                    question_id=question_id,
                    selected_answer=None,
                    is_correct=False,
                    marks_awarded=0.0,
                    time_taken_seconds=0,
                )

                db.add(answer)

                continue

            # -------------------------------------------------
            # EMPTY ANSWER
            # -------------------------------------------------

            if not answer.selected_answer:

                answer.is_correct = False

                answer.marks_awarded = 0.0

                continue

            # -------------------------------------------------
            # CHECK CORRECTNESS
            # -------------------------------------------------

            correct_answer = (
                question.correct_answer
                .strip()
                .upper()
            )

            selected_answer = (
                answer.selected_answer
                .strip()
                .upper()
            )

            is_correct = (
                selected_answer
                == correct_answer
            )

            answer.is_correct = (
                is_correct
            )

            # -------------------------------------------------
            # CORRECT
            # -------------------------------------------------

            if is_correct:

                answer.marks_awarded = (
                    question.marks or 0.0
                )

                score += (
                    question.marks or 0.0
                )

                correct += 1

            # -------------------------------------------------
            # INCORRECT
            # -------------------------------------------------

            else:

                negative_marks = (
                    question.negative_marks or 0.0
                )

                answer.marks_awarded = (
                    -negative_marks
                )

                score -= (
                    negative_marks
                )

        # =====================================================
        # SAVE GENERATED ANSWERS
        # =====================================================

        db.flush()

        # =====================================================
        # GET FINAL ANSWERS
        # =====================================================

        final_answers = (
            db.query(ExamAnswer)
            .filter(
                ExamAnswer.session_id
                == session_id
            )
            .all()
        )

        # =====================================================
        # COUNTS
        # =====================================================

        attempted = sum(
            1
            for answer in final_answers
            if answer.selected_answer
        )

        incorrect = sum(
            1
            for answer in final_answers
            if answer.selected_answer
            and not answer.is_correct
        )

        unanswered = (
            session.total_questions
            - attempted
        )

        accuracy = (
            (
                correct
                / attempted
            )
            * 100
            if attempted
            else 0.0
        )

        # =====================================================
        # TIME USED
        # =====================================================

        time_used = sum(
            answer.time_taken_seconds or 0
            for answer in final_answers
        )

        # =====================================================
        # UPDATE SESSION
        # =====================================================

        session.total_marks = round(
            total_marks,
            2,
        )

        session.score = round(
            score,
            2,
        )

        session.accuracy = round(
            accuracy,
            2,
        )

        session.submitted_at = (
            datetime.utcnow()
        )

        session.status = "submitted"

        db.commit()

        db.refresh(session)

        # =====================================================
        # CREATE ATTEMPTS
        # =====================================================

        ExamService._create_attempts(
            db=db,
            user_id=user_id,
            session_id=session_id,
            answers=final_answers,
        )

        # =====================================================
        # UPDATE MASTERY
        # =====================================================

        ExamService._update_mastery(
            db=db,
            user_id=user_id,
            questions=questions,
        )

        # =====================================================
        # RETURN RESULT
        # =====================================================

        return {
            "session": session,
            "answers": final_answers,
            "attempted": attempted,
            "correct": correct,
            "incorrect": incorrect,
            "unanswered": unanswered,
            "time_used": time_used,
        }

    # =========================================================
    # CREATE ATTEMPTS
    # =========================================================

    @staticmethod
    def _create_attempts(
        db: Session,
        user_id: int,
        session_id: int,
        answers: list[ExamAnswer],
    ):
        """
        Creates exactly one Attempt for every
        answered question in this exam session.

        Exam attempts do not have a confidence value because
        the current exam-answer flow does not collect confidence.
        """

        created_count = 0

        for answer in answers:

            # -------------------------------------------------
            # IGNORE UNANSWERED QUESTIONS
            # -------------------------------------------------

            if not answer.selected_answer:
                continue

            # -------------------------------------------------
            # CHECK DUPLICATE
            # -------------------------------------------------

            existing = (
                db.query(Attempt)
                .filter(
                    Attempt.user_id
                    == user_id,

                    Attempt.question_id
                    == answer.question_id,

                    Attempt.session_id
                    == session_id,
                )
                .first()
            )

            if existing:
                continue

            # -------------------------------------------------
            # CREATE ATTEMPT
            # -------------------------------------------------

            attempt = Attempt(
                user_id=user_id,

                question_id=answer.question_id,

                session_id=session_id,

                selected_answer=(
                    answer.selected_answer
                ),

                is_correct=(
                    answer.is_correct
                ),

                time_taken_seconds=(
                    answer.time_taken_seconds
                    or 0
                ),

                # Exam currently does not collect
                # confidence from the student.
                confidence=None,

                created_at=(
                    answer.answered_at
                    or datetime.utcnow()
                ),
            )

            db.add(attempt)

            created_count += 1

        db.commit()

        print(
            f"[EXAM ATTEMPTS] "
            f"session={session_id}, "
            f"created={created_count}"
        )

    # =========================================================
    # UPDATE MASTERY
    # =========================================================

    @staticmethod
    def _update_mastery(
        db: Session,
        user_id: int,
        questions: dict[int, Question],
    ):
        """
        Recalculates mastery for every topic represented
        in the exam.
        """

        topic_ids = set()

        for question in questions.values():

            if question.topic_id:

                topic_ids.add(
                    question.topic_id
                )

        print(
            f"[EXAM MASTERY] "
            f"Updating topics={list(topic_ids)}"
        )

        for topic_id in topic_ids:

            try:

                mastery = (
                    MasteryService.calculate_topic_mastery(
                        db=db,
                        user_id=user_id,
                        topic_id=topic_id,
                    )
                )

                if mastery:

                    print(
                        f"[EXAM MASTERY] "
                        f"topic={topic_id}, "
                        f"mastery={mastery.mastery_score}, "
                        f"accuracy={mastery.accuracy}"
                    )

            except Exception as exc:

                print(
                    "Mastery update failed "
                    f"for topic {topic_id}: {exc}"
                )

    # =========================================================
    # TOPIC PERFORMANCE
    # =========================================================

    @staticmethod
    def get_topic_performance(
        db: Session,
        session_id: int,
    ):

        rows = (
            db.query(
                Question.topic_id,
                Topic.name,
                ExamAnswer.selected_answer,
                ExamAnswer.is_correct,
                ExamAnswer.marks_awarded,
            )
            .join(
                ExamAnswer,
                ExamAnswer.question_id
                == Question.id,
            )
            .join(
                Topic,
                Topic.id
                == Question.topic_id,
            )
            .filter(
                ExamAnswer.session_id
                == session_id
            )
            .all()
        )

        performance = {}

        for row in rows:

            topic_id = row.topic_id

            if topic_id not in performance:

                performance[
                    topic_id
                ] = {
                    "topic_id": topic_id,
                    "topic": row.name,
                    "total_questions": 0,
                    "attempted": 0,
                    "correct": 0,
                    "marks": 0.0,
                }

            item = performance[
                topic_id
            ]

            item[
                "total_questions"
            ] += 1

            if row.selected_answer:

                item[
                    "attempted"
                ] += 1

            if row.is_correct:

                item[
                    "correct"
                ] += 1

            item[
                "marks"
            ] += (
                row.marks_awarded
                or 0.0
            )

        result = []

        for item in performance.values():

            attempted = item[
                "attempted"
            ]

            item[
                "accuracy"
            ] = (
                (
                    item["correct"]
                    / attempted
                )
                * 100
                if attempted
                else 0.0
            )

            item[
                "marks"
            ] = round(
                item["marks"],
                2,
            )

            item[
                "accuracy"
            ] = round(
                item["accuracy"],
                2,
            )

            result.append(item)

        return result