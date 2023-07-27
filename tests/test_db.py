import pytest
from datetime import datetime
from sqlalchemy import select

from chatcmd.db.models import User, Message

from .database import LocalDatabase, SQLALCHEMY_DATABASE_URL
from .factories import UserFactory, MessageFactory, get_test_user_password


@pytest.mark.asyncio
async def test_get_user():
    username = "gvard"
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    test_session = db.get_test_session()

    UserFactory.set_session(test_session)
    UserFactory.create(name=username)
    await test_session.commit()

    user = await db.get_user_by_name(username)
    assert user.name == username

    await test_session.close()


@pytest.mark.asyncio
async def test_add_user():
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    await db.add_user("gvard", "abc123!@#")
    test_session = db.get_test_session()

    users = await test_session.execute(select(User))
    assert len(users.all()) == 1

    await test_session.close()


@pytest.mark.asyncio
async def test_login_user():
    username = "gvard"
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    test_session = db.get_test_session()

    UserFactory.reset_sequence()
    UserFactory.set_session(test_session)
    UserFactory.create(name=username)
    await test_session.commit()
    users = await test_session.execute(select(User))
    password = get_test_user_password(users.scalar_one())

    login = await db.login_user(username, password)
    assert login == True

    await test_session.close()


@pytest.mark.asyncio
async def test_get_messages():
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    test_session = db.get_test_session()

    UserFactory.set_session(test_session)
    MessageFactory.set_session(test_session)
    MessageFactory.create_batch(10)
    await test_session.commit()

    messages = await db.get_messages(12, 0, datetime.now())
    assert len(messages) == 10

    await test_session.close()


@pytest.mark.asyncio
async def test_add_message():
    username = "gvard"
    db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
    await db.recreate_tables()
    test_session = db.get_test_session()

    UserFactory.set_session(test_session)
    UserFactory.create(name=username)
    await test_session.commit()
    await db.add_message(username, "hello everyone")

    messages = await test_session.execute(select(Message))
    assert len(messages.all()) == 1

    await test_session.close()
