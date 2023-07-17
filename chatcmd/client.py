import os
import sys
import termios
import tty
import logging
import asyncio
from asyncio import StreamReader, StreamWriter
from collections import deque

from .reader import *
from .utils import *
from .store import MessageStore


class MessageError(Exception):
    pass


class ChatClient:
    def __init__(self) -> None:
        self._server_writer: StreamWriter
        self._server_reader: StreamReader
        self._stdin_reader: StreamReader
        self._messages: MessageStore
        self._ack_event = asyncio.Event()
        self._send_event = asyncio.Event()

    async def _send_message(self, message: str):
        max_retries = 3
        for i in range(max_retries + 1):
            try:
                self._server_writer.write((message + "\n").encode())
                await self._server_writer.drain()
                await asyncio.wait_for(self._ack_event.wait(), 2 + i)
                break
            except asyncio.exceptions.TimeoutError:
                if i == max_retries:
                    raise MessageError
                else:
                    await self._messages.append(
                        f"Could not send the message, retrying...({i+1}/{max_retries})\n"
                    )

    async def _listen_for_messages(self):  # A
        while (message := await self._server_reader.readline()) != b"":
            message_str = message.decode()

            if self._send_event and "\ACK" in message_str:
                self._ack_event.set()
            else:
                await self._messages.append(message_str)

        await self._messages.append("Server closed connection.")

    async def _read_and_send(self):  # B
        while True:
            message = await read_line(self._stdin_reader)
            try:
                self._send_event.set()
                await self._send_message(message)
            except MessageError:
                await self._messages.append("Failed to send the message\n")
                sys.stdout.flush()
            finally:
                self._ack_event.clear()
                self._send_event.clear()

    async def _redraw_output(self, items: deque):
        save_cursor_position()
        move_to_top_of_screen()
        for item in items:
            delete_line()
            sys.stdout.write(item)
        restore_cursor_position()

    async def start_chat_client(self):
        # switch terminal to raw mode to avoid race conditions
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        os.system("clear")
        rows = move_to_bottom_of_screen()

        self._messages = MessageStore(self._redraw_output, rows - 1)

        self._stdin_reader = await create_stdin_reader()
        sys.stdout.write("Enter username: ")
        sys.stdout.flush()
        username = await read_line(self._stdin_reader)

        try:
            self._server_reader, self._server_writer = await asyncio.open_connection(
                "127.0.0.1", 8000
            )  # C
        except:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            sys.stdout.write("Could not connect to server\n")
            return

        self._server_writer.write(f"CONNECT {username}\n".encode())
        await self._server_writer.drain()

        message_listener = asyncio.create_task(self._listen_for_messages())  # D
        input_listener = asyncio.create_task(self._read_and_send())

        try:
            _, pending = await asyncio.wait(
                [message_listener, input_listener], return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
        except Exception as e:
            logging.exception(e)
            self._server_writer.close()
            await self._server_writer.wait_closed()
        finally:
            sys.stdout.flush()
            # switch terminal back to echo mode
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


async def main():
    chat_client = ChatClient()
    await chat_client.start_chat_client()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Interrupted by user")
