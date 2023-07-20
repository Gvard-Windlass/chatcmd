import pytest_asyncio
import sqlalchemy as sa
from .database import engine, test_session_factory

# these fixtures set up the db once and then
# never actually commit anything to it,
# so we can have clean db for each test run


# This fixture creates a nested
# transaction, recreates it when the application code calls session.commit
# and rolls it back at the end.
# Based on: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest_asyncio.fixture()
async def session():
    connection = await engine.connect()
    transaction = await connection.begin()
    session = test_session_factory(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = await connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sa.event.listens_for(session.sync_session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    await session.close()
    await transaction.rollback()
    await connection.close()
