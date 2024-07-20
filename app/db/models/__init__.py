from datetime import datetime
from typing import Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(10), nullable=False, unique=True)
    password = mapped_column(String(10), nullable=False)
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    chat_histories = relationship("ChatHistory", back_populates="user")


class ChatHistory(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    chatmessage = mapped_column(String(1000))
    create_date: Mapped[datetime] = mapped_column(insert_default=func.now())
    user = relationship("user", back_populates="chat_histories")
