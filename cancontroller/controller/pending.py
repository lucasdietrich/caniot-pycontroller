import asyncio
import contextlib
import time
from typing import List

import can

from cancontroller.caniot.models import MsgId


class PendingQuery:
    def __init__(self, query: MsgId):
        self.event = asyncio.Event()
        self.query = query
        self.response_id = None
        self.response = None

    def is_set(self) -> bool:
        if self.event.is_set():
            if self.response_id is None:
                raise Exception("event is set but response is not set")
            return True
        return False

    def check(self, response_id: MsgId, response: can.Message) -> bool:
        if response_id.is_response_of(self.query):
            self.response_id = response_id
            self.response = response
            self.event.set()
            return True
        else:
            return False


class PendingQueriesManager:
    def __init__(self):
        self.pending_queries: List[PendingQuery] = []

    async def wait_for_response(self, pending_query: PendingQuery, timeout: float) -> [bool, float]:
        self.pending_queries.append(pending_query)

        start = time.time()
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(pending_query.event.wait(), timeout)
        duration = time.time() - start

        self.pending_queries.remove(pending_query)

        return pending_query.event.is_set(), duration

    def process(self, response_id: MsgId, response: can.Message):
        for query in self.pending_queries:
            if query.check(response_id, response):
                break