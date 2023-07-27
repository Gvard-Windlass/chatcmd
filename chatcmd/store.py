from collections import deque
from typing import Callable, Awaitable


class MessageStore:
    def __init__(self, callback: Callable[[deque], Awaitable[None]]):
        self._messages = []
        self._past_messages = []
        # callback will be responsible for redrawing the output
        self._callback = callback

    async def append(self, message):
        self._messages.append(message)
        await self._callback(self._past_messages + self._messages)

    async def extend(self, message_list: list[str]):
        self._past_messages = message_list + self._past_messages
        await self._callback(self._past_messages + self._messages)

    def get_len(self):
        return len(self._messages) + len(self._past_messages)
