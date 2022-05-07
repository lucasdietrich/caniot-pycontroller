import asyncio
from typing import List

from cancontroller.caniot.message.message import CaniotMessage


class PendingQuery:
    def __init__(self, query: CaniotMessage, expect_count: int = None):
        if query.msgid.is_broadcast_device():
            self.expect_count = int(expect_count) if expect_count else -1
        else:
            self.expect_count = 1

        self.event = asyncio.Event()
        self.query: CaniotMessage = query
        self.responses: List[CaniotMessage] = []
        self.count = 0

    def is_set(self) -> bool:
        if self.event.is_set():
            if not self.responses:
                raise Exception("event is set but response is not set")
            return True
        return False

    def eval(self, response: CaniotMessage):
        if response.msgid.is_response_of(self.query.msgid):
            self.responses.append(response)
            self.count += 1

            if self.count == self.expect_count:
                self.event.set()

            return True
        else:
            return False