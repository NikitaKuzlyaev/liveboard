# tasks.py
# app/tasks/tasks.py

import logging
from app.db.models import Room
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from celery import shared_task
from uuid import UUID
from app.db.database import get_db
from app.db.database import SessionLocal

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from app.tasks.celery_app import celery_app


@celery_app.task
def delete_room_task(room_uuid: UUID):
    logger.info(f"Task delete_room_task started for room_id: {room_uuid}")
    print('here')

    db = SessionLocal()
    logger.info("Database session created")  # Логирование создания сессии

    try:
        room = db.get(Room, room_uuid)
        logger.info(f"Fetched room: {room}")  # Логируем полученную комнату

        if room:
            logger.info(f"Room found, deleting room with id: {room.uuid}")
            db.delete(room)
            db.commit()
            logger.info(f"Room with id {room.uuid} deleted successfully")
        else:
            logger.warning(f"Room with id {room_uuid} not found")
    except Exception as e:
        logger.error(f"Error during delete_room_task: {e}")
        db.rollback()
    finally:
        db.close()
        logger.info("Database session closed")  # Логируем закрытие сессии

