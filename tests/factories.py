import factory

from chatcmd.db.models import User, Message
from chatcmd.db.pwd import get_password_hash

test_password_base = "Bk7^31&3LDXt"


def get_test_user_password(user: User):
    return f"{test_password_base}{int(user.id)-1}"


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def set_session(cls, session):
        cls._meta.sqlalchemy_session = session


class UserFactory(BaseFactory):
    class Meta:
        model = User

    name = factory.Faker("name")
    password_hash = factory.Sequence(
        lambda n: get_password_hash(f"{test_password_base}{n}")
    )


class MessageFactory(BaseFactory):
    class Meta:
        model = Message

    text = factory.Faker("paragraph", nb_sentences=2)
    user = factory.SubFactory(UserFactory)
