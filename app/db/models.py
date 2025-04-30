from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, func

Base = declarative_base()

"""
alembic revision --autogenerate -m "db change"
alembic upgrade head


"""


class Room(Base):
    __tablename__ = "rooms"

    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    is_open = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("site_users.id"))

    room_users = relationship("RoomUser", back_populates="room", foreign_keys="RoomUser.room_id")


class RoomUser(Base):
    __tablename__ = "room_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.uuid"))

    room = relationship("Room", back_populates="room_users", foreign_keys=[room_id])


class SiteUser(Base):
    __tablename__ = "site_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_registration_complete = Column(Boolean, default=False)
    hashed_password = Column(String)


class RegistrationConfirmation(Base):
    __tablename__ = "regs_confirms"

    id = Column(Integer, primary_key=True, index=True)
    validation_string = Column(String, index=True, unique=True)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=False)
