from sqlalchemy.orm import Session

from chatcmd.db.models import User, Message

from .fixtures import session
from .factories import UserFactory, MessageFactory


def test_user_model(session: Session):
    UserFactory.set_session(session)
    UserFactory.create_batch(3)
    session.commit()
    users = session.query(User).all()
    assert len(users) == 3


def test_message_model(session: Session):
    UserFactory.set_session(session)
    MessageFactory.set_session(session)

    MessageFactory.create_batch(5)
    session.commit()
    messages = session.query(Message).all()
    assert len(messages) == 5
