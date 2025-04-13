from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()


class Room(Base):
    __tablename__ = "rooms"

    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    is_open = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"))

    # Указываем, что внешним ключом для связи с пользователями является room_id из модели User
    users = relationship("User", back_populates="room", foreign_keys="[User.room_id]")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.uuid"))

    # Указываем, что внешним ключом для связи с комнатой является room_id
    room = relationship("Room", back_populates="users", foreign_keys=[room_id])
