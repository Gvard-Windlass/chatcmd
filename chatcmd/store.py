from collections import deque
from typing import Callable, Awaitable


class MessageStore:
    def __init__(self, callback: Callable[[deque], Awaitable[None]]):
        self._messages = []
        # callback will be responsible for redrawing the output
        self._callback = callback

    async def append(self, message):
        self._messages.append(message)
        await self._callback(self._messages)

    async def extend(self, message_list: list[str]):
        self._messages = message_list + self._messages
        await self._callback(self._messages)
