from __future__ import annotations

import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    messages: Mapped[list[Message]] = relationship(
        "Message", back_populates="user", lazy="subquery"
    )


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(
        "User", back_populates="messages", lazy="subquery"
    )
