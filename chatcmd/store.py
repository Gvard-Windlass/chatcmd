from collections import deque
from typing import Callable, Awaitable


class MessageStore:
    def __init__(
        self, callback: Callable[[deque], Awaitable[None]], max_size: int = 100
    ):
        self._messages: deque = deque(maxlen=max_size)
        # callback will be responsible for redrawing the output
        self._callback = callback

    async def append(self, message):
        self._messages.append(message)
        await self._callback(self._messages)
