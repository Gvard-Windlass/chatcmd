import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chatcmd.db.models import User, Message

from .fixtures import session
from .factories import UserFactory, MessageFactory


@pytest.mark.asyncio
async def test_user_model(session: AsyncSession):
    UserFactory.set_session(session)

    UserFactory.create_batch(3)
    await session.commit()

    users = await session.execute(select(User))
    assert len(users.all()) == 3


@pytest.mark.asyncio
async def test_message_model(session: AsyncSession):
    UserFactory.set_session(session)
    MessageFactory.set_session(session)

    MessageFactory.create_batch(5)
    await session.commit()

    messages = await session.execute(select(Message))
    assert len(messages.all()) == 5
