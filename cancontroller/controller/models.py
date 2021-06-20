from __future__ import annotations

from enum import Enum, IntEnum
from dataclasses import dataclass

from typing import Union

import can

DEVICE_BROADCAST = 0b111111

data_type_size = [
    8,
    1,
    4,
    4,
    8,
    8,
    8,
    0
]

@dataclass
class MsgId:
    class IdType(IntEnum):
        Standard: int = 11
        Extended: int = 29

    class FrameType(IntEnum):
        Command: int = 0
        Telemetry: int = 1
        WriteAttribute: int = 2
        ReadAttribute: int = 3
    frame_type: FrameType

    class QueryType(IntEnum):
        Query: int = 0
        Response: int = 1
    query_type: QueryType

    class Controller(IntEnum):
        Main: int = 0
        Controller1: int = 1
        Controller2: int = 2
        BROADCAST: int = 3

    controller: Controller

    class DataType(IntEnum):
        U: int = 0
        CR: int = 1
        CRA: int = 2
        CRT: int = 3
        CRTTA: int = 4
        CRTAAA: int = 5
        TTTT: int = 6
        _: int = 7

    data_type: DataType
    device_id: int

    @staticmethod
    def from_raw(value: int) -> MsgId:
        return MsgId(
            MsgId.FrameType(value & 0b11),
            MsgId.QueryType((value >> 2) & 1),
            MsgId.Controller((value >> 3) & 0b11),
            MsgId.DataType((value >> 5) & 0b111),
            (value >> 8) & 0b111,
        )

    def __repr__(self):
        return f"{self.query_type.name} {self.frame_type.name} between {self.controller.name} and D{self.device_id} [{self.data_type.name}]"

    def __int__(self) -> int:
        return self.get()

    def get(self) -> int:
        return self.frame_type | self.query_type << 2 | self.controller << 3 | self.data_type << 5 | self.device_id << 8

    def bin_repr(self) -> str:
        return bin(int(self))[2:].rjust(11, "0")


def send_garage_can_command(relay: int) -> can.Message:
    arbitration_id = MsgId(
        frame_type=MsgId.FrameType.Command,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.BROADCAST,
        data_type=MsgId.DataType.CRT,
        device_id=0
    )
    print(arbitration_id, hex(int(arbitration_id)))
    return can.Message(arbitration_id=int(arbitration_id),
    is_extended_id=False,
    data=[1 << relay, 0, 0, 0])


if __name__ == "__main__":
    msgid = MsgId(
        frame_type=MsgId.FrameType.Telemetry,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.BROADCAST,
        data_type=MsgId.DataType.CRT,
        device_id=0
    )

    print(msgid, ":", msgid.bin_repr()) 