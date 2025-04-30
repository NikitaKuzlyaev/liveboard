from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Room
import uuid


async def create_room(session: AsyncSession) -> Room:
    new_room = Room(uuid=uuid.uuid4(), is_open=True)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room
