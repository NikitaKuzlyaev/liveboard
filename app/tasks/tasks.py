from .celery_app import celery_app
from db.models import Room  # импортируй свою модель комнаты
from db.database import get_db  # зависит от твоего проекта
from sqlalchemy.orm import Session
from sqlalchemy.future import select


@celery_app.task
def delete_room_task(room_id: int):
    db: Session = next(get_db())
    room = db.get(Room, room_id)
    if room:
        db.delete(room)
        db.commit()
