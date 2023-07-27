# chatcmd
Practice project made from sample async command-line chat app provided in [this book](https://github.com/concurrency-in-python-with-asyncio/concurrency-in-python-with-asyncio) (chapter 8).

**Currently works only on linux** (tested on WSL).

## Working with project
Can be run either with postgres or sqlite.

To set up and run this project, follow the instructions:
1. Clone this repo by runnig 

`https://github.com/Gvard-Windlass/chatcmd.git`

2. Create virtual environment and install project dependencies using [poetry](https://python-poetry.org/):
   - `poetry shell`
   - `poetry install`

3. [optional] Create .env file in `chatcmd/db` folder with your PostgreSQL credentials:

```
POSTGRES_USER="your_username"
POSTGRES_PASSWORD="your_password"
```

4. [optional] Initialize postgres database: 
   - Create database `chat`
   - Apply [alembic](https://alembic.sqlalchemy.org/en/latest/) migrations: `alembic upgrade heads`

5. Run server with `python -m chatcmd.server` for `postgres `or `python -m chatcmd.server run_local` for `sqlite`


6. Run one or multiple clients with `python -m chatcmd.client`