from __future__ import annotations

import struct
from enum import Enum, IntEnum
from dataclasses import dataclass

import random

from typing import Union, List, Dict, Tuple

import can

# ____________________________________________________________________________________________________________________ #

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

        def get_size(self) -> int:
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
            assert 0 < self < len(data_type_size)
            return self.data_type_size[self]

    data_type: Union[int, DataType]
    sub_id: int

    @classmethod
    def from_int(cls, deviceid: int) -> DeviceId:
        return DeviceId(
            data_type=DeviceId.DataType(deviceid & 7),
            sub_id=(deviceid >> 3) & 7
        )

    def get_id(self) -> int:
        return (self.sub_id << 3) | self.data_type

    id = property(get_id)

    def __eq__(self, other: Union[int, DeviceId]):
        return other == int(self)

    def __int__(self):
        return self.get_id()

    def __repr__(self):
        if self.get_id() == 0:
            return "Undefined DeviceId=0"
        else:
            return f"DeviceId={self.get_id()} (data_type = {self.data_type.name} [{self.data_type.value}], sub_id={self.sub_id})"

    @classmethod
    def Undefined(cls) -> DeviceId:
        return DeviceId(data_type=DeviceId.DataType.U, sub_id=0)

    @classmethod
    def Broadcast(cls) -> DeviceId:
        return DeviceId(data_type=DeviceId.DataType._, sub_id=0b111)


DEVICE_BROADCAST = DeviceId.Broadcast()


# ____________________________________________________________________________________________________________________ #


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

    class Controller(IntEnum):
        Main = 0           # Main controller also get all CAN messages
        Controller1 = 1    # Mean Controller1 + Main controller
        Controller2 = 2    # Mean Controller2 + Main controller
        BROADCAST = 3      # Mean All Controllers, main controller + controllers 1 & 2

        def join(self, controller: MsgId.Controller):
            return self | controller

    controller: Controller

    device_id: DeviceId

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
                   f"between {MsgId.Controller(self.controller).name} " \
                   f"and {self.device_id}"
        elif self.is_error():
            return f"[{hex(self)}] ERROR message from {self.device_id} to {MsgId.Controller(self.controller).name}"
        else:
            raise NotImplemented

    def __int__(self) -> int:
        return self.get()

    def __index__(self):
        return int(self)

    def __and__(self, other: MsgId):
        return int(self) & int(other)

    def get(self) -> int:
        std_id = self.frame_type | self.query_type << 2 | self.controller << 3 | self.device_id.get_id() << 5

        if self.id_type is MsgId.IdType.Extended:
            return std_id | self.extended_id << 11
        else:
            return std_id

    @staticmethod
    def from_int(value: int, extended: bool = None) -> MsgId:
        return MsgId(
            MsgId.FrameType(value & 0b11),
            MsgId.QueryType((value >> 2) & 1),
            MsgId.Controller((value >> 3) & 0b11),
            device_id=DeviceId.from_int(value >> 5),
            extended_id=value >> 11 if extended is None or extended is True else 0,
            id_type=MsgId.IdType.Extended if value >> 11 and extended is not False else MsgId.IdType.Standard
        )

    def bin_repr(self) -> str:
        return bin(int(self))[2:].rjust(self.id_type, "0")

    def is_error(self) -> bool:
        return self.frame_type == MsgId.FrameType.Command and self.query_type == MsgId.QueryType.Response

    def is_valid(self) -> bool:
        return self.device_id != 0 and not self.is_error()

    def is_query(self) -> bool:
        return self.is_valid() and self.query_type is MsgId.QueryType.Query

    def is_response(self) -> bool:
        return self.is_valid() and self.query_type is MsgId.QueryType.Response

    def prepare_response(self, controllers: int = None) -> MsgId:
        if self.is_query():
            if self.frame_type == MsgId.FrameType.Command:
                raise Exception(f"cannot build a response for a QueryCommand : {self}")
            else:
                return MsgId(
                    frame_type=self.frame_type,
                    query_type=MsgId.QueryType.Response,
                    controller=MsgId.Controller(self.controller if controllers is None else (controllers | self.controller)),
                    device_id=self.device_id,
                    id_type=self.id_type,
                    extended_id=self.extended_id if self.id_type is MsgId.IdType.Extended else 0
                )
        else:
            raise Exception(f"{self} MsgID is not a query")

    def is_response_of(self, query: MsgId) -> bool:
        if self.is_valid():
            virtual_response = query.prepare_response(None)
            virtual_response.controller = self.controller

            return all([
                self.controller & query.controller == query.controller,
                self == virtual_response
            ])
        else:
            raise Exception(f"{query} is not a valid Query")

    def is_query_of(self, response: MsgId) -> bool:
        return response.is_response_of(self)

    def is_extended(self) -> bool:
        return self.id_type is MsgId.IdType.Extended

    @classmethod
    def Query(cls, device: DeviceId, controller: Controller = Controller.BROADCAST, extended_id: int = 0) -> MsgId:
        return MsgId(
            frame_type=MsgId.FrameType.Telemetry,
            query_type=MsgId.QueryType.Query,
            controller=MsgId.Controller(controller),
            device_id=device,
            extended_id=extended_id,
            id_type=MsgId.IdType.Extended if extended_id else MsgId.IdType.Standard
        )

    @classmethod
    def ReadAttribute(cls, device: DeviceId, controller: Controller = Controller.BROADCAST, extended_id: int = 0) -> MsgId:
        msgid = MsgId.Query(device, controller, extended_id)
        msgid.frame_type = MsgId.FrameType.ReadAttribute
        return msgid

    @classmethod
    def WriteAttribute(cls, device: DeviceId, controller: Controller = Controller.BROADCAST, extended_id: int = 0) -> MsgId:
        msgid = MsgId.Query(device, controller, extended_id)
        msgid.frame_type = MsgId.FrameType.WriteAttribute
        return msgid

    @classmethod
    def QueryTelemetry(cls, device: DeviceId, controller: Controller = Controller.BROADCAST, extended_id: int = 0) -> MsgId:
        msgid = MsgId.Query(device, controller, extended_id)
        msgid.frame_type = MsgId.FrameType.Telemetry
        return msgid

    @classmethod
    def Command(cls, device: DeviceId, controller: Controller = Controller.BROADCAST, extended_id: int = 0) -> MsgId:
        msgid = MsgId.Query(device, controller, extended_id)
        msgid.frame_type = MsgId.FrameType.Command
        return msgid

# ____________________________________________________________________________________________________________________ #


class ControllerMessageBuilder:
    def __init__(
            self,
            controller: MsgId.Controller = MsgId.Controller.Main,
            controller_policy: MsgId.Controller = MsgId.Controller.BROADCAST
    ):
        self.controller = controller
        self.controller_policy: MsgId.Controller = MsgId.Controller(controller_policy)
        self.extended_id = 0
        self.extended_id_policy = False

    def gen_extended_id(self) -> int:
        return random.randint(0, 0xFF)

    def build_can_message(self, device: DeviceId, frame_type: MsgId.FrameType, data: Union[List[int], bytearray, bytes] = b"") -> Tuple[MsgId, can.Message]:
        msgid = MsgId(
            frame_type=frame_type,
            query_type=MsgId.QueryType.Query,
            controller=self.controller.join(self.controller_policy),
            device_id=device,
            extended_id=self.gen_extended_id() if self.extended_id_policy else 0,
            id_type=MsgId.IdType.Extended if self.extended_id_policy else MsgId.IdType.Standard
        )

        if msgid.is_query():
            return msgid, can.Message(
                arbitration_id=int(msgid),
                data=data,
                is_extended_id=msgid.is_extended()
            )
        else:
            raise Exception(f"built can message isn't a valid query {msgid}")

    # https://docs.python.org/3/library/struct.html#format-characters
    def ReadAttribute(self, device: DeviceId, key: int) -> Tuple[MsgId, can.Message]:
        data = struct.pack("<H", key & 0xFFFF)
        return self.build_can_message(device, MsgId.FrameType.ReadAttribute, data)

    def WriteAttribute(self, device: DeviceId, key: int, value: int) -> Tuple[MsgId, can.Message]:
        data = struct.pack("<HL", key & 0xFFFF, value & 0xFFFFFFFF)
        return self.build_can_message(device, MsgId.FrameType.WriteAttribute, data)

    def Command(self, device: DeviceId, data: Union[List[int], bytearray, bytes]) -> Tuple[MsgId, can.Message]:
        data_len = len(data)
        expected_data_len = device.data_type.get_size()
        if data_len != expected_data_len:
            raise Exception(f"invalid data size ({data_len}) for the DataType {device.data_type.name} ({expected_data_len})")

        return self.build_can_message(device, MsgId.FrameType.Command, data)

    def QueryTelemetry(self, device: DeviceId) -> Tuple[MsgId, can.Message]:
        return self.build_can_message(device, MsgId.FrameType.Telemetry)


class ControllerMessageParser:
    @staticmethod
    def ParseAttributeResponse(data) -> [int, int]:
        return struct.unpack("<HL", data)

# ____________________________________________________________________________________________________________________ #


def gen_garage_can_command(relay: int, proddev = 0, prodtype = DeviceId.DataType.CRT) -> can.Message:
    arbitration_id = MsgId(
        frame_type=MsgId.FrameType.Command,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.BROADCAST,
        device_id=DeviceId(data_type=prodtype, sub_id=proddev)
    )
    return can.Message(arbitration_id=int(arbitration_id),
                       is_extended_id=False,
                       data=[0, relay, 0, 0]
                       )


# ____________________________________________________________________________________________________________________ #


if __name__ == "__main__":
    msgid = MsgId(
        frame_type=MsgId.FrameType.Telemetry,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.Controller2,
        device_id=DeviceId(DeviceId.DataType.CRT, 1)
    )

    print(msgid, ":", msgid.bin_repr())
