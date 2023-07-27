from chatcmd.db.db_queries import Database
from chatcmd.db.models import Base


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///tests/test.sqlite3"


class LocalDatabase(Database):
    async def recreate_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    def get_test_session(self):
        return self._async_session()
