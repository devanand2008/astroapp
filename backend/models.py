from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String, nullable=True)
    role = Column(String, default="User") # "User", "Astrologer", "Admin"
    status = Column(String, default="Approved") # "Approved", "Pending", "Rejected"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages_sent = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    astrologer_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="chat_room")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    msg_type = Column(String, default="text") # text, voice
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
