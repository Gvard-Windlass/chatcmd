from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .models import Message, User
from .pwd import get_password_hash, verify_password


class Database:
    def __init__(
        self,
        database_url: str,
    ) -> None:
        self._engine = create_async_engine(database_url)
        self._async_session = async_sessionmaker(self._engine)

    async def get_messages(self, amount: int, before: datetime):
        async with self._async_session() as session:
            stmt = (
                select(Message)
                .filter(Message.timestamp < before)
                .order_by(Message.timestamp.asc())
                .limit(amount)
            )
            result = await session.execute(stmt)
            return result.scalars().all()

    async def add_message(self, username: str, text: str):
        user = await self.get_user_by_name(username)
        msg = Message(text=text, user_id=user.id)
        async with self._async_session() as session:
            session.add(msg)
            await session.commit()

    async def get_user_by_name(self, username: str):
        async with self._async_session() as session:
            stmt = select(User).where(User.name == username)
            result = await session.execute(stmt)
            return result.scalar()

    async def add_user(self, username: str, password: str):
        pwd_hash = get_password_hash(password)
        user = User(name=username, password_hash=pwd_hash)
        async with self._async_session() as session:
            session.add(user)
            await session.commit()

    async def login_user(self, username: str, password: str):
        async with self._async_session() as session:
            stmt = select(User).where(User.name == username)
            result = await session.execute(stmt)
            user = result.scalar()
            if user and verify_password(password, user.password_hash):
                return True
            return False
