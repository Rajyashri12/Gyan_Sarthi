from datetime import datetime

from sqlalchemy.orm import Session

from app.models.diagnostic_session import DiagnosticSession
from app.models.diagnostic_answer import DiagnosticAnswer
from app.models.question import Question
from app.models.subject import Subject
from app.models.topic import Topic

from app.services.diagnostic_mastery_service import (
    DiagnosticMasteryService,
)


class DiagnosticService:

    # ============================================================
    # START DIAGNOSTIC
    # ============================================================

    @staticmethod
    def start_diagnostic(
        db: Session,
        user_id: int,
        exam_id: int,
        questions_per_subject: int = 5,
    ):
        """
        Create a diagnostic assessment.

        Questions are selected subject-wise so that the assessment
        covers all available subjects for the selected exam.
        """

        if questions_per_subject < 1:
            questions_per_subject = 1

        if questions_per_subject > 20:
            questions_per_subject = 20

        # --------------------------------------------------------
        # Find subjects belonging to this exam
        # --------------------------------------------------------

        subjects = (
            db.query(Subject)
            .filter(
                Subject.exam_id == exam_id
            )
            .order_by(Subject.id.asc())
            .all()
        )

        if not subjects:
            raise ValueError(
                "No subjects found for this exam."
            )

        selected_questions = []

        # --------------------------------------------------------
        # Select questions from each subject
        # --------------------------------------------------------

        for subject in subjects:

            questions = (
                db.query(Question)
                .filter(
                    Question.exam_id == exam_id,
                    Question.subject_id == subject.id,
                )
                .order_by(Question.id.asc())
                .limit(questions_per_subject)
                .all()
            )

            selected_questions.extend(
                questions
            )

        # --------------------------------------------------------
        # No questions available
        # --------------------------------------------------------

        if not selected_questions:
            raise ValueError(
                "No questions found for this diagnostic assessment."
            )

        # --------------------------------------------------------
        # Create diagnostic session
        # --------------------------------------------------------

        session = DiagnosticSession(
            user_id=user_id,
            exam_id=exam_id,
            total_questions=len(selected_questions),
            started_at=datetime.utcnow(),
            status="in_progress",
            score=0.0,
            accuracy=0.0,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return {
            "session": session,
            "questions": selected_questions,
        }

    # ============================================================
    # SAVE ANSWER
    # ============================================================

    @staticmethod
    def save_answer(
        db: Session,
        user_id: int,
        session_id: int,
        question_id: int,
        selected_answer: str | None,
        time_taken_seconds: int = 0,
    ):
        """
        Save or update a student's diagnostic answer.
        """

        # --------------------------------------------------------
        # Find session
        # --------------------------------------------------------

        session = (
            db.query(DiagnosticSession)
            .filter(
                DiagnosticSession.id == session_id,
                DiagnosticSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            raise ValueError(
                "Diagnostic session not found."
            )

        # --------------------------------------------------------
        # Check session status
        # --------------------------------------------------------

        if session.status != "in_progress":
            raise ValueError(
                "This diagnostic session is already completed."
            )

        # --------------------------------------------------------
        # Find question
        # --------------------------------------------------------

        question = (
            db.query(Question)
            .filter(
                Question.id == question_id,
                Question.exam_id == session.exam_id,
            )
            .first()
        )

        if not question:
            raise ValueError(
                "Question does not belong to this diagnostic exam."
            )

        # --------------------------------------------------------
        # Normalize selected answer
        # --------------------------------------------------------

        normalized_answer = None

        if selected_answer is not None:

            normalized_answer = (
                selected_answer
                .strip()
                .upper()
            )

            if normalized_answer == "":
                normalized_answer = None

        # --------------------------------------------------------
        # Normalize time
        # --------------------------------------------------------

        if time_taken_seconds is None:
            time_taken_seconds = 0

        if time_taken_seconds < 0:
            time_taken_seconds = 0

        # --------------------------------------------------------
        # Determine correctness
        # --------------------------------------------------------

        is_correct = False

        if normalized_answer is not None:

            correct_answer = (
                question.correct_answer
                .strip()
                .upper()
            )

            is_correct = (
                normalized_answer == correct_answer
            )

        # --------------------------------------------------------
        # Check if answer already exists
        # --------------------------------------------------------

        answer = (
            db.query(DiagnosticAnswer)
            .filter(
                DiagnosticAnswer.session_id == session_id,
                DiagnosticAnswer.question_id == question_id,
            )
            .first()
        )

        # --------------------------------------------------------
        # Update existing answer
        # --------------------------------------------------------

        if answer:

            answer.selected_answer = normalized_answer
            answer.is_correct = is_correct
            answer.time_taken_seconds = time_taken_seconds
            answer.answered_at = datetime.utcnow()

        # --------------------------------------------------------
        # Create new answer
        # --------------------------------------------------------

        else:

            answer = DiagnosticAnswer(
                session_id=session_id,
                question_id=question_id,
                selected_answer=normalized_answer,
                is_correct=is_correct,
                time_taken_seconds=time_taken_seconds,
                answered_at=datetime.utcnow(),
            )

            db.add(answer)

        db.commit()
        db.refresh(answer)

        return {
            "session_id": session_id,
            "question_id": question_id,
            "selected_answer": normalized_answer,
            "saved": True,
        }

    # ============================================================
    # COMPLETE DIAGNOSTIC
    # ============================================================

    @staticmethod
    def complete_diagnostic(
        db: Session,
        user_id: int,
        session_id: int,
    ):
        """
        Complete the diagnostic assessment.

        Pipeline:

            Diagnostic Answers
                    ↓
              Score Calculation
                    ↓
             Topic Performance
                    ↓
              Initial Mastery
                    ↓
              Final Response
        """

        # --------------------------------------------------------
        # Find diagnostic session
        # --------------------------------------------------------

        session = (
            db.query(DiagnosticSession)
            .filter(
                DiagnosticSession.id == session_id,
                DiagnosticSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            raise ValueError(
                "Diagnostic session not found."
            )

        # --------------------------------------------------------
        # Get answers
        # --------------------------------------------------------

        answers = (
            db.query(DiagnosticAnswer)
            .filter(
                DiagnosticAnswer.session_id == session_id
            )
            .all()
        )

        # --------------------------------------------------------
        # Get corresponding questions
        # --------------------------------------------------------

        question_ids = [
            answer.question_id
            for answer in answers
        ]

        questions = {}

        if question_ids:

            question_list = (
                db.query(Question)
                .filter(
                    Question.id.in_(question_ids)
                )
                .all()
            )

            questions = {
                question.id: question
                for question in question_list
            }

        # --------------------------------------------------------
        # Counters
        # --------------------------------------------------------

        attempted = 0
        correct = 0
        incorrect = 0
        unanswered = 0

        score = 0.0

        # --------------------------------------------------------
        # Evaluate every answer
        # --------------------------------------------------------

        for answer in answers:

            question = questions.get(
                answer.question_id
            )

            if not question:
                continue

            # ----------------------------------------------------
            # Unanswered
            # ----------------------------------------------------

            if (
                answer.selected_answer is None
                or answer.selected_answer.strip() == ""
            ):

                unanswered += 1
                answer.is_correct = False

                continue

            # ----------------------------------------------------
            # Attempted
            # ----------------------------------------------------

            attempted += 1

            selected_answer = (
                answer.selected_answer
                .strip()
                .upper()
            )

            correct_answer = (
                question.correct_answer
                .strip()
                .upper()
            )

            # ----------------------------------------------------
            # Correct
            # ----------------------------------------------------

            if selected_answer == correct_answer:

                correct += 1
                answer.is_correct = True

                score += question.marks

            # ----------------------------------------------------
            # Incorrect
            # ----------------------------------------------------

            else:

                incorrect += 1
                answer.is_correct = False

                score -= question.negative_marks

        # --------------------------------------------------------
        # Calculate accuracy
        # --------------------------------------------------------

        if attempted > 0:

            accuracy = (
                correct / attempted
            ) * 100

        else:

            accuracy = 0.0

        # --------------------------------------------------------
        # Update diagnostic session
        # --------------------------------------------------------

        session.score = round(
            score,
            2
        )

        session.accuracy = round(
            accuracy,
            2
        )

        session.status = "completed"

        session.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(session)

        # --------------------------------------------------------
        # Topic-wise performance
        # --------------------------------------------------------

        topic_results = (
            DiagnosticService.get_topic_results(
                db=db,
                session_id=session_id,
            )
        )

        # --------------------------------------------------------
        # INITIAL MASTERY
        # --------------------------------------------------------

        mastery_results = (
            DiagnosticMasteryService.initialize_mastery(
                db=db,
                user_id=user_id,
                session_id=session_id,
            )
        )

        # --------------------------------------------------------
        # Final database commit
        # --------------------------------------------------------

        db.commit()

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Return direct fields.
        #
        # DO NOT return:
        #
        # {
        #     "session": session
        # }
        #
        # The route expects session_id, exam_id, etc.
        # --------------------------------------------------------

        return {
            "session_id": session.id,
            "exam_id": session.exam_id,
            "total_questions": session.total_questions,
            "attempted": attempted,
            "correct": correct,
            "incorrect": incorrect,
            "unanswered": unanswered,
            "score": round(score, 2),
            "accuracy": round(accuracy, 2),
            "topic_results": topic_results,
            "initial_mastery": mastery_results,
        }

    # ============================================================
    # GET TOPIC RESULTS
    # ============================================================

    @staticmethod
    def get_topic_results(
        db: Session,
        session_id: int,
    ):
        """
        Generate topic-wise diagnostic performance.
        """

        rows = (
            db.query(
                DiagnosticAnswer,
                Question,
                Topic,
            )
            .join(
                Question,
                DiagnosticAnswer.question_id == Question.id,
            )
            .join(
                Topic,
                Question.topic_id == Topic.id,
            )
            .filter(
                DiagnosticAnswer.session_id == session_id
            )
            .all()
        )

        topic_data = {}

        # --------------------------------------------------------
        # Group answers by topic
        # --------------------------------------------------------

        for answer, question, topic in rows:

            topic_id = topic.id

            if topic_id not in topic_data:

                topic_data[topic_id] = {
                    "topic_id": topic.id,
                    "topic": topic.name,
                    "total_questions": 0,
                    "attempted": 0,
                    "correct": 0,
                }

            topic_data[topic_id][
                "total_questions"
            ] += 1

            # ----------------------------------------------------
            # Attempted
            # ----------------------------------------------------

            if (
                answer.selected_answer is not None
                and answer.selected_answer.strip() != ""
            ):

                topic_data[topic_id][
                    "attempted"
                ] += 1

                # ------------------------------------------------
                # Correct
                # ------------------------------------------------

                if answer.is_correct:

                    topic_data[topic_id][
                        "correct"
                    ] += 1

        # --------------------------------------------------------
        # Convert to response format
        # --------------------------------------------------------

        results = []

        for data in topic_data.values():

            attempted = data["attempted"]
            correct = data["correct"]

            if attempted > 0:

                accuracy = (
                    correct / attempted
                ) * 100

            else:

                accuracy = 0.0

            results.append({
                "topic_id": data["topic_id"],
                "topic": data["topic"],
                "total_questions": data["total_questions"],
                "attempted": attempted,
                "correct": correct,
                "accuracy": round(
                    accuracy,
                    2
                ),
            })

        # --------------------------------------------------------
        # Sort by topic
        # --------------------------------------------------------

        results.sort(
            key=lambda item: item["topic_id"]
        )

        return results