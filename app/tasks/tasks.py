# tasks.py
# app/tasks/tasks.py

import logging
from uuid import UUID

from app.db.database import SessionLocal
from app.db.models import Room
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@celery_app.task
def delete_room_task(room_uuid: UUID):
    db = SessionLocal()

    try:
        room = db.get(Room, room_uuid)

        if room:
            db.delete(room)
            db.commit()

    except Exception as e:
        logger.error(f"Error during delete_room_task: {e}")
        db.rollback()
    finally:
        db.close()
