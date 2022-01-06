from __future__ import annotations

from cancontroller.caniot.models import MsgId, DeviceId, BufferType

from abc import ABC

import can


class CaniotMessage(ABC):
    """
    Represent a caniot message
    """

    @property
    def arbitration_id(self):
        return int(self.msgid)

    def __init__(self, msgid: MsgId, buffer: BufferType = None):
        if buffer is None:
            buffer = []

        self.msgid = msgid

        assert len(buffer) <= 8
        self.buffer = list(buffer)

    def __repr__(self):
        return f"{self.msgid} : {self.buffer}"

    def get_arbitration_id(self):
        return self.msgid

    @classmethod
    def from_can(cls, canmsg: can.Message) -> CaniotMessage:
        return CaniotMessage(
            msgid=MsgId.from_int(canmsg.arbitration_id, extended=False),
            buffer=canmsg.data
        )

    def can(self) -> can.Message:
        return can.Message(arbitration_id=int(self.arbitration_id),
                           is_extended_id=False,
                           data=self.buffer)

    def is_response_of(self,  query: CaniotMessage):
        return self.msgid.is_response_of(query.msgid)


class ErrorMessage(CaniotMessage):
    pass