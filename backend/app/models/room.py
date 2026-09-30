from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    max_capacity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    supported_modules = relationship("RoomModule", back_populates="room")

class RoomModule(Base):
    __tablename__ = "room_modules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("therapy_modules.id"), nullable=False)
    room = relationship("Room", back_populates="supported_modules")
