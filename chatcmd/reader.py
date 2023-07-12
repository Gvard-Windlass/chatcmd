import sys
import asyncio
from asyncio import StreamReader
from collections import deque

from .utils import move_back_one_char, clear_screen


async def create_stdin_reader() -> StreamReader:
    stream_reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(stream_reader)
    loop = asyncio.get_running_loop()
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return stream_reader


async def read_line(stdin_reader: StreamReader) -> str:
    def erase_last_char():
        move_back_one_char()
        sys.stdout.write(" ")
        move_back_one_char()

    delete_char = b"\x7f"
    input_buffer: deque = deque()
    while (input_char := await stdin_reader.read(1)) != b"\n":
        if input_char == delete_char:
            if len(input_buffer) > 0:
                input_buffer.pop()
                erase_last_char()
                sys.stdout.flush()
        else:
            input_buffer.append(input_char)
            sys.stdout.write(input_char.decode())
            sys.stdout.flush()
    clear_screen()
    return b"".join(input_buffer).decode()
