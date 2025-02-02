import asyncio
import collections


class Queue:
    def __init__(self, maxsize: int = 0):
        self._maxsize = maxsize
        self._deque = collections.deque((), maxsize)
        self._event = asyncio.Event()

    def put_nowait(self, item):
        # Add the item to the right side of the deque
        # If the deque is full, the oldest item will be removed
        self._deque.append(item)
        # Notify any waiting tasks that an item has been added
        self._event.set()

    async def get(self):
        # Wait until an item is available in the deque
        while not self._deque:
            self._event.clear()
            await self._event.wait()

        # Remove and return the leftmost item from the deque
        return self._deque.popleft()

    def qsize(self) -> int:
        return len(self._deque)


class SimpleQueue:
    def __init__(self, size=0):
        self._items = []
        self._event = asyncio.Event()
        self.size = size

    async def get(self):
        while not self._items:
            self._event.clear()
            await self._event.wait()
        return self._items.pop(0)

    async def put(self, item):
        if self.size and len(self._items) >= self.size:
            self._items.pop(0)
        self._items.append(item)
        self._event.set()
