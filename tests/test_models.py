import pytest
from sqlalchemy import select

from chatcmd.db.models import User, Message

from .database import LocalDatabase, SQLALCHEMY_DATABASE_URL
from .factories import UserFactory, MessageFactory


@pytest.mark.asyncio
async def test_user_model():
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    test_session = db.get_test_session()

    UserFactory.set_session(test_session)

    UserFactory.create_batch(3)
    await test_session.commit()

    users = await test_session.execute(select(User))
    assert len(users.all()) == 3

    await test_session.close()


@pytest.mark.asyncio
async def test_message_model():
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    test_session = db.get_test_session()

    UserFactory.set_session(test_session)
    MessageFactory.set_session(test_session)

    MessageFactory.create_batch(5)
    await test_session.commit()

    messages = await test_session.execute(select(Message))
    assert len(messages.all()) == 5

    await test_session.close()
