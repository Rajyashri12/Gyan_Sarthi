import logging
import sys
from pathlib import Path

# Ensure 'backend' directory is on sys.path regardless of execution context
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select
from app.database.database import Base, SessionLocal, engine
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.topic import Topic
from app.database.seed.gate_syllabus import GATE_SYLLABUS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def seed_database() -> None:
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    gate_data = GATE_SYLLABUS.get("GATE")
    if not gate_data:
        logger.error("Key 'GATE' not found in GATE_SYLLABUS.")
        return

    # Use session context manager to automatically manage commit/rollback/close
    with SessionLocal() as db:
        with db.begin():
            # -------------------------
            # Exam
            # -------------------------
            exam = db.scalar(
                select(Exam).where(Exam.code == gate_data["code"])
            )
            if not exam:
                exam = Exam(
                    name=gate_data["name"],
                    code=gate_data["code"],
                    description=gate_data.get(
                        "description", 
                        "GATE Computer Science and Information Technology"
                    ),
                )
                db.add(exam)
                db.flush()
                logger.info(f"Created Exam: {exam.name} ({exam.code})")

            # -------------------------
            # Subjects
            # -------------------------
            for subject_data in gate_data.get("subjects", []):
                subject = db.scalar(
                    select(Subject).where(
                        Subject.exam_id == exam.id,
                        Subject.code == subject_data["code"],
                    )
                )
                if not subject:
                    subject = Subject(
                        exam_id=exam.id,
                        name=subject_data["name"],
                        code=subject_data["code"],
                    )
                    db.add(subject)
                    db.flush()
                    logger.info(f"  Added Subject: {subject.name} [{subject.code}]")

                # -------------------------
                # Topics & Subtopics
                # -------------------------
                for topic_data in subject_data.get("topics", []):
                    topic = db.scalar(
                        select(Topic).where(
                            Topic.subject_id == subject.id,
                            Topic.name == topic_data["name"],
                            Topic.parent_topic_id.is_(None),
                        )
                    )
                    if not topic:
                        topic = Topic(
                            subject_id=subject.id,
                            name=topic_data["name"],
                            parent_topic_id=None,
                        )
                        db.add(topic)
                        db.flush()

                    for subtopic_name in topic_data.get("subtopics", []):
                        subtopic = db.scalar(
                            select(Topic).where(
                                Topic.subject_id == subject.id,
                                Topic.name == subtopic_name,
                                Topic.parent_topic_id == topic.id,
                            )
                        )
                        if not subtopic:
                            subtopic = Topic(
                                subject_id=subject.id,
                                name=subtopic_name,
                                parent_topic_id=topic.id,
                            )
                            db.add(subtopic)

    logger.info("GATE syllabus seeded successfully.")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as exc:
        logger.exception("Database seeding encountered an unexpected error.")
        sys.exit(1)