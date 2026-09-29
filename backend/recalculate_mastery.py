from app.database.database import SessionLocal
from app.services.mastery_service import MasteryService

db = SessionLocal()

try:
    user_id = 2

    topic_ids = [71, 80]

    for topic_id in topic_ids:

        mastery = MasteryService.calculate_topic_mastery(
            db=db,
            user_id=user_id,
            topic_id=topic_id,
        )

        if mastery:
            print(
                f"Topic {topic_id}: "
                f"mastery={mastery.mastery_score}, "
                f"accuracy={mastery.accuracy}, "
                f"confidence={mastery.confidence_score}"
            )

finally:
    db.close()