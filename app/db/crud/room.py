from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Room, SiteUser
import uuid
from uuid import UUID
from uuid import uuid4
from typing import List
from sqlalchemy.future import select
from pydantic import BaseModel




async def create_room(
        session: AsyncSession,
        user: SiteUser,
) -> Room:
    """
    """
    new_room = Room(uuid=uuid.uuid4(), is_open=True, creator_id=user.id)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room


async def get_room_by_uuid(
        session: AsyncSession,
        room_uuid: UUID,
) -> Room:
    """
    """
    result = await session.execute(select(Room).filter(Room.uuid == room_uuid))
    room = result.scalar_one_or_none()
    return room


async def get_list_of_rooms_by_user(
        session: AsyncSession,
        user: SiteUser,
) -> List[UUID]:
    """
    """
    result = await session.execute(select(Room).filter(Room.creator_id == user.id))
    rooms = result.scalars().all()
    room_uuids = [room.uuid for room in rooms]
    return room_uuids
