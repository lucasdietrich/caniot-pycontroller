from __future__ import annotations

from enum import Enum, IntEnum
from dataclasses import dataclass

from typing import Union, List, Dict, Tuple

BufferType = Union[List[int], bytearray, bytes]


@dataclass
class DeviceId:
    class Class(IntEnum):
        CUSTOMPCB: int = 0
        C1: int = 1
        C2: int = 2
        C3: int = 3
        C4: int = 4
        C5: int = 5
        C6: int = 6
        C7: int = 7
        # U: int = 0
        # CR: int = 1
        # CRA: int = 2
        # CRT: int = 3
        # CRTTA: int = 4
        # CRTAAA: int = 5
        # TTTT: int = 6
        # _: int = 7
        CLSBROADCAST: int = 0b111 # shadow class name for broadcast

        def get_size(self, ep: MsgId.Endpoint = 0) -> int:
            data_type_size = [
                8,
                # 1,
                # 4,
                # 4,
                # 8,
                # 8,
                # 8,
                # 0
            ]
            assert 0 <= self < len(data_type_size)
            return data_type_size[self]

    def __init__(self, cls: Union[int, Class], sid: int):
        self.cls = cls
        self.sid = sid

    def set_cls(self, cls: Union[int, Class]):
        self._cls = DeviceId.Class(cls)

    def get_cls(self) -> Class:
        return self._cls

    _cls: Class
    sid: int

    cls: Class = property(get_cls, set_cls)

    @classmethod
    def from_int(cls, deviceid: int) -> DeviceId:
        return DeviceId(
            cls=DeviceId.Class(deviceid & 7),
            sid=(deviceid >> 3) & 7
        )

    def get_id(self) -> int:
        return (self.sid << 3) | self.cls

    id = property(get_id)

    def __eq__(self, other: Union[int, DeviceId]):
        return int(other) == int(self)

    def __int__(self):
        return self.get_id()

    def is_broadcast(self) -> bool:
        return self.sid == 0x7 and self.cls == 0x7

    def __repr__(self):
        if self.is_broadcast():
            return "Broadcast (sid=0x7, cls = 0x7)"
        else:
            cls = DeviceId.Class(self.cls)
            return f"DeviceId={self.get_id()} (cls = {cls.name} [{cls.value}], sid={self.sid})"

    @classmethod
    def Broadcast(cls) -> DeviceId:
        return DeviceId(cls=DeviceId.Class.CLSBROADCAST, sid=0b111)


@dataclass
class MsgId:
    class IdType(IntEnum):
        Standard = 11
        Extended = 29

    class FrameType(IntEnum):
        Command = 0
        Telemetry = 1
        WriteAttribute = 2
        ReadAttribute = 3

    frame_type: FrameType

    class QueryType(IntEnum):
        Query = 0
        Response = 1

    query_type: QueryType

    device_id: DeviceId

    class Endpoint(IntEnum):

        AppDefaultEndpoint = 0
        Endpoint1 = 1
        Endpoint2 = 2
        BoardControlEndpoint = 3

        def join(self, controller: MsgId.Endpoint):
            return self | controller

    endpoint: Endpoint = Endpoint.AppDefaultEndpoint

    extended_id: int = 0

    id_type: IdType = IdType.Standard

    def __eq__(self, other: Union[int, MsgId]):
        return int(self) == int(other)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.is_valid():
            return f"[{hex(self)}] " \
                   f"{MsgId.QueryType(self.query_type).name} " \
                   f"{MsgId.FrameType(self.frame_type).name} " \
                   f"{MsgId.Endpoint(self.endpoint).name} " \
                   f"{self.device_id}"
        elif self.is_error():
            return f"[{hex(self)}] ERROR message from {self.device_id}"
        else:
            return f"INVALID CANIOT MESSAGE [0x{int(self):04X}]"

    def __int__(self) -> int:
        return self.get()

    def __index__(self):
        return int(self)

    def __and__(self, other: MsgId):
        return int(self) & int(other)

    def get(self) -> int:
        std_id = self.frame_type | self.query_type << 2 | self.device_id.get_id() << 3 | self.endpoint << 9

        if self.id_type is MsgId.IdType.Extended:
            return std_id | self.extended_id << 11
        else:
            return std_id

    @staticmethod
    def from_int(value: int, extended: bool = None) -> MsgId:
        return MsgId(
            frame_type=MsgId.FrameType(value & 0b11),
            query_type=MsgId.QueryType((value >> 2) & 1),
            device_id=DeviceId.from_int((value >> 3) & 0b111111),
            endpoint=MsgId.Endpoint((value >> 9) & 0b11),
            extended_id=value >> 11 if extended is None or extended is True else 0,
            id_type=MsgId.IdType.Extended if value >> 11 and extended is not False else MsgId.IdType.Standard
        )

    def bin_repr(self) -> str:
        return bin(int(self))[2:].rjust(self.id_type, "0")

    def is_error(self) -> bool:
        return self.frame_type == MsgId.FrameType.Command and self.query_type == MsgId.QueryType.Response

    def is_valid(self) -> bool:
        return self.device_id != 0 and not self.is_error() and \
               (self.query_type == MsgId.QueryType.Query or not self.is_broadcast_device()) # cannot be a response from all nodes

    def is_query(self) -> bool:
        return self.is_valid() and self.query_type is MsgId.QueryType.Query

    def is_broadcast_device(self) -> bool:
        return self.device_id == DeviceId.Broadcast()

    def is_response(self) -> bool:
        return self.is_valid() and self.query_type is MsgId.QueryType.Response

    def prepare_response(self) -> MsgId:
        if self.is_query():
            if self.frame_type == MsgId.FrameType.Command:
                resp_type = MsgId.FrameType.Telemetry
            elif self.frame_type == MsgId.FrameType.WriteAttribute:
                resp_type = MsgId.FrameType.ReadAttribute
            else:
                resp_type = self.frame_type

            return MsgId(
                frame_type=resp_type,
                query_type=MsgId.QueryType.Response,
                endpoint=self.endpoint,
                device_id=self.device_id,
                id_type=self.id_type,
                extended_id=self.extended_id if self.id_type is MsgId.IdType.Extended else 0
            )
        else:
            raise Exception(f"{self} MsgID is not a query")

    def is_response_of(self, query: MsgId) -> bool:

        if self.is_valid():
            expected_response = query.prepare_response()

            # handle the case when a message is a response for a broadcast message
            if query.is_broadcast_device():

                # we expect a response to a broadcast query
                expected_response.device_id = self.device_id

            return expected_response == self
        else:
            raise Exception(f"{query} is not a valid Query")

    def is_query_of(self, response: MsgId) -> bool:
        return response.is_response_of(self)

    def is_extended(self) -> bool:
        return self.id_type is MsgId.IdType.Extended

# ____________________________________________________________________________________________________________________ #


if __name__ == "__main__":
    msgid = MsgId(
        frame_type=MsgId.FrameType.Telemetry,
        query_type=MsgId.QueryType.Query,
        endpoint=MsgId.Endpoint.AppDefaultEndpoint,
        device_id=DeviceId(DeviceId.Class.CUSTOMPCB, 1)
    )

    print(msgid, ":", msgid.bin_repr())
