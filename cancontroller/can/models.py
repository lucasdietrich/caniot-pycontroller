from enum import Enum, IntEnum
from dataclasses import dataclass

from typing import Union


@dataclass
class DeviceId:
    class DataType(IntEnum):
        U: int = 0
        CR: int = 1
        CRA: int = 2
        CRT: int = 3
        CRTTA: int = 4
        CRTAAA: int = 5
        TTTT: int = 6
        _: int = 7

    data_type: Union[int, DataType]

    sub_id: int

    def get_id(self) -> int:
        return (self.data_type << 3) | self.sub_id

    id = property(get_id)

    def __int__(self):
        return self.id

    def __repr__(self):
        return f"DeviceId={self.id} (data_type = {self.data_type.name} [{self.data_type.value}], sub_id={self.sub_id})"

DEVICE_BROADCAST = DeviceId(DeviceId.DataType._, 7)

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

    frame_type: Union[int, FrameType]

    class QueryType(IntEnum):
        Query: int = 0
        Response: int = 1

    query_type: Union[int, QueryType]

    class Controller(IntEnum):
        Main: int = 0
        Controller1: int = 1
        Controller2: int = 2
        BROADCAST: int = 3

    controller: Union[int, Controller]

    device_id: DeviceId

    id_type: IdType = IdType.Standard

    def __repr__(self):
        return f"{self.query_type.name} {self.frame_type.name} between {self.controller.name} and {self.device_id}"

    def __int__(self) -> int:
        return self.get()

    def get(self) -> int:
        return self.frame_type | self.query_type << 2 | self.controller << 3 | self.device_id.get_id() << 5

    def bin_repr(self) -> str:
        return bin(int(self))[2:].rjust(self.id_type, "0")


if __name__ == "__main__":
    msgid = MsgId(
        frame_type=MsgId.FrameType.Telemetry,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.BROADCAST,
        device_id=DeviceId(DeviceId.DataType.CRTAAA, 5)
    )

    print(msgid, ":", msgid.bin_repr()) 