import uuid
from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CHAR, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(CHAR(36), primary_key=True, default=uuid.uuid4)
    username = mapped_column(String(10), nullable=False, unique=True)
    password = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    conversation = relationship("Conversation", back_populates="user")


class Conversation(db.Model):
    id: Mapped[int] = mapped_column(CHAR(36), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    user = relationship("User", back_populates="conversation")
    message = relationship("Message", back_populates="conversation")


class Message(db.Model):
    id: Mapped[int] = mapped_column(CHAR(36), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversation.id"), nullable=False
    )

    sender = mapped_column(String(100))
    chat_message = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())

    conversation = relationship("Conversation", back_populates="message")
