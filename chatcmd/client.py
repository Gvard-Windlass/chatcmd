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


async def send_message(message: str, writer: StreamWriter):
    writer.write((message + "\n").encode())
    await writer.drain()


async def listen_for_messages(reader: StreamReader, message_store: MessageStore):  # A
    while (message := await reader.readline()) != b"":
        await message_store.append(message.decode())
    await message_store.append("Server closed connection.")


async def read_and_send(stdin_reader: StreamReader, writer: StreamWriter):  # B
    while True:
        message = await read_line(stdin_reader)
        await send_message(message, writer)


async def main():
    async def redraw_output(items: deque):
        save_cursor_position()
        move_to_top_of_screen()
        for item in items:
            delete_line()
            sys.stdout.write(item)
        restore_cursor_position()

    # switch terminal to raw mode to avoid race conditions
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    os.system("clear")
    rows = move_to_bottom_of_screen()

    messages = MessageStore(redraw_output, rows - 1)

    stdin_reader = await create_stdin_reader()
    sys.stdout.write("Enter username: ")
    sys.stdout.flush()
    username = await read_line(stdin_reader)

    reader, writer = await asyncio.open_connection("127.0.0.1", 8000)  # C

    writer.write(f"CONNECT {username}\n".encode())
    await writer.drain()

    message_listener = asyncio.create_task(listen_for_messages(reader, messages))  # D
    input_listener = asyncio.create_task(read_and_send(stdin_reader, writer))

    try:
        await asyncio.wait(
            [message_listener, input_listener], return_when=asyncio.FIRST_COMPLETED
        )
    except Exception as e:
        logging.exception(e)
        writer.close()
        await writer.wait_closed()
    finally:
        # switch terminal back to echo mode
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# if __name__ == "main":
#     asyncio.run(main())
asyncio.run(main())
