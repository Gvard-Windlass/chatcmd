import asyncio
import logging
import re
import json
from datetime import datetime
from asyncio import StreamReader, StreamWriter
import sys
from .db.db_queries import Database
from .db.db_config import get_settings
from .validators import validate_password, validate_username

from tests.database import LocalDatabase, SQLALCHEMY_DATABASE_URL


class CredentialsError(Exception):
    pass


class ChatServer:
    def __init__(self, run_local: bool):
        self._username_to_writer: dict[str, StreamWriter] = {}
        if run_local:
            self._db = LocalDatabase(SQLALCHEMY_DATABASE_URL)
            print("Running local database")
        else:
            settings = get_settings()
            if not settings.env_set():
                raise EnvironmentError(
                    "Could not find necessary env variables, got: ",
                    settings.describe_env(),
                )
            self._db = Database(settings.DATABASE_URL)
            print("Running server database")

    async def start_chat_server(self, host: str, port: int):
        if type(self._db) == LocalDatabase:
            await self._db.recreate_tables()

        server = await asyncio.start_server(self.client_connected, host, port)

        async with server:
            await server.serve_forever()

    # Wait for the client to provide a valid username command; otherwise, disconnect them.
    async def client_connected(self, reader: StreamReader, writer: StreamWriter):  # A
        command = await reader.readline()
        print(f"CONNECTED {reader} {writer}")

        try:
            command, name, pwd = command.decode().strip().split(" ")
            if command != "CONNECT":
                raise ValueError
        except:
            await self._reject_client(
                writer,
                client_message="Invalid command.\n",
                server_message="Got invalid command from client, disconnecting.",
            )
            return

        user = await self._db.get_user_by_name(name)
        try:
            if user:
                await self._login_user(writer, name, pwd)
            else:
                await self._register_user(writer, name, pwd)
        except CredentialsError:
            await self._reject_client(
                writer,
                client_message="Invalid credentials.\n",
                server_message="Client authentication failed, disconnecting",
            )
            return

        self._add_user(name, reader, writer)
        await self._on_connect(name, writer)

    async def _reject_client(
        self,
        writer: StreamWriter,
        client_message: str | None = None,
        server_message: str | None = None,
    ):
        if server_message:
            logging.error(server_message)
        if client_message:
            writer.write(client_message.encode())
            await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def _login_user(self, writer: StreamWriter, username: str, password: str):
        login = await self._db.login_user(username, password)
        if not login:
            raise CredentialsError
        writer.write("Login successful\n".encode())
        await writer.drain()

    async def _register_user(self, writer: StreamWriter, username: str, password: str):
        valid_pwd = validate_password(password)
        valid_name = validate_username(username)
        if not valid_pwd or not valid_name:
            raise CredentialsError
        await self._db.add_user(username, password)
        writer.write("Registration successful\n".encode())
        await writer.drain()

    # Store a user’s stream writer instance and create a task to listen for messages.
    def _add_user(self, username: str, reader: StreamReader, writer: StreamWriter):  # B
        self._username_to_writer[username] = writer
        asyncio.create_task(self._listen_for_messages(username, reader))

    # Once a user connects, notify all others that they have connected.
    async def _on_connect(self, username: str, writer: StreamWriter):  # C
        writer.write(
            f"Welcome! {len(self._username_to_writer)} user(s) are online!\n".encode()
        )
        await writer.drain()
        await self._notify_all(f"{username} connected!\n")

    async def _remove_user(self, username: str):
        writer = self._username_to_writer[username]
        del self._username_to_writer[username]
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logging.exception("Error closing client writer, ignoring.", exc_info=e)

    # Listen for messages from a client and send them to all other clients, waiting a maximum of a minute for a message.
    async def _listen_for_messages(self, username: str, reader: StreamReader):  # D
        try:
            while (data := await asyncio.wait_for(reader.readline(), 60)) != b"":
                await self._process_message(username, data.decode())
            await self._notify_all(f"{username} has left the chat\n")
        except asyncio.exceptions.TimeoutError as e:
            print(f"Client {username} timed out")
            await self._remove_user(username)
        except Exception as e:
            logging.exception("Error reading from client.", exc_info=e)
            await self._remove_user(username)

    async def _process_message(self, username: str, message: str):
        if re.match(r"\\LOAD", message):
            await self._acknowledge(username)
            _, amount = message.strip().split(" ")
            messages = await self._db.get_messages(int(amount), datetime.now())
            prep_messages = [f"{x.user.name}: {x.text}" for x in messages]
            messages_json = "\PACK " + json.dumps(prep_messages) + "\n"
            writer = self._username_to_writer[username]
            writer.write(messages_json.encode())
            await writer.drain()
        if re.match(r"\\[q|Q]", message):
            await self._acknowledge(username)
            print(f"Closing {username} connection")
            await self._remove_user(username)
        else:
            await self._db.add_message(username, message)
            await self._acknowledge(username)
            await self._notify_all(f"{username}: {message}")

    async def _acknowledge(self, username: str):
        writer = self._username_to_writer[username]
        writer.write(f"\ACK\n".encode())
        await writer.drain()

    # Send a message to all connected clients, removing any disconnected users.
    async def _notify_all(self, message: str):  # E
        inactive_users = []
        for username, writer in self._username_to_writer.items():
            try:
                writer.write(message.encode())
                await writer.drain()
            except ConnectionError as e:
                logging.exception("Could not write to client.", exc_info=e)
                inactive_users.append(username)

        [await self._remove_user(username) for username in inactive_users]


async def main():
    try:
        run_local = "run_local" in sys.argv
        chat_server = ChatServer(run_local)
    except EnvironmentError as e:
        print(e)
        return
    await chat_server.start_chat_server("127.0.0.2", 8000)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nInterrupted by user")
