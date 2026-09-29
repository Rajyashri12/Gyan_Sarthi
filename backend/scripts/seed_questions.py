import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.database import Base, engine, SessionLocal
from app.models.question import Question
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic


BASE_DIR = Path(__file__).resolve().parents[2]

QUESTION_DIRECTORIES = [
    BASE_DIR / "data" / "questions" / "gate" / "dbms",
    BASE_DIR / "data" / "questions" / "gate" / "os",
    BASE_DIR / "data" / "questions" / "gate" / "cn",
    BASE_DIR / "data" / "questions" / "gate" / "general_aptitude",
]


def find_topic(
    db: Session,
    subject_id: int,
    topic_name: str,
):
    return (
        db.query(Topic)
        .filter(
            Topic.subject_id == subject_id,
            Topic.name.ilike(topic_name),
            Topic.parent_topic_id.is_(None),
        )
        .first()
    )


def find_subtopic(
    db: Session,
    subject_id: int,
    parent_topic_id: int,
    subtopic_name: str,
):
    if not subtopic_name:
        return None

    return (
        db.query(Topic)
        .filter(
            Topic.subject_id == subject_id,
            Topic.parent_topic_id == parent_topic_id,
            Topic.name.ilike(subtopic_name),
        )
        .first()
    )


def seed_file(
    db: Session,
    file_path: Path,
):
    if not file_path.exists():
        return 0

    # Using utf-8-sig to automatically strip any UTF-8 BOM headers
    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
    ) as file:
        questions = json.load(file)

    subject_code = file_path.parent.name

    exam = (
        db.query(Exam)
        .filter(
            Exam.code == "GATE_CSE"
        )
        .first()
    )

    if not exam:
        raise ValueError(
            "GATE_CSE exam not found. "
            "Run seed_database.py first."
        )

    subject = (
        db.query(Subject)
        .filter(
            Subject.exam_id == exam.id,
            Subject.code == subject_code.upper(),
        )
        .first()
    )

    if not subject:
        print(f"Subject not found: {subject_code}")
        return 0

    count = 0

    for data in questions:
        topic = find_topic(
            db,
            subject.id,
            data["topic"],
        )

        if not topic:
            print(f"Topic not found: {data['topic']}")
            continue

        subtopic = find_subtopic(
            db,
            subject.id,
            topic.id,
            data.get("subtopic"),
        )

        question = Question(
            exam_id=exam.id,
            subject_id=subject.id,
            topic_id=topic.id,
            subtopic_id=subtopic.id if subtopic else None,
            question_text=data["question_text"],
            option_a=data.get("option_a"),
            option_b=data.get("option_b"),
            option_c=data.get("option_c"),
            option_d=data.get("option_d"),
            correct_answer=data["correct_answer"],
            explanation=data.get("explanation"),
            difficulty=data.get("difficulty", "medium"),
            question_type=data.get("question_type", "MCQ"),
            is_pyq=data.get("is_pyq", False),
            exam_year=data.get("exam_year"),
            marks=data.get("marks", 1.0),
            negative_marks=data.get("negative_marks", 0.0),
            source=data.get("source"),
        )

        db.add(question)
        count += 1

    return count


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        total = 0
        for directory in QUESTION_DIRECTORIES:
            file_path = directory / "questions.json"
            count = seed_file(db, file_path)
            total += count

        db.commit()
        print(f"\nSuccessfully seeded {total} questions.")

    finally:
        db.close()


if __name__ == "__main__":
    main()