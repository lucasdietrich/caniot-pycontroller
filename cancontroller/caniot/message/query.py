from abc import ABC

from .message import CaniotMessage
from cancontroller.caniot.models import BufferType, MsgId, DeviceId
from cancontroller.caniot.misc import fit_buffer
from cancontroller.caniot.datatypes import XPS

import struct

class ReadAttributeQuery(CaniotMessage):
    def __init__(self, deviceid: DeviceId, key: int):
        super(ReadAttributeQuery, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.ReadAttribute,
                query_type=MsgId.QueryType.Query,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=struct.pack("<H", key & 0xFFFF)
        )


class WriteAttributeQuery(CaniotMessage):
    def __init__(self, deviceid: DeviceId, key: int, value: int):
        super(WriteAttributeQuery, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.WriteAttribute,
                query_type=MsgId.QueryType.Query,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=struct.pack("<HL", key & 0xFFFF, value & 0xFFFFFFFF)
        )


class Command(CaniotMessage):
    def __init__(self, deviceid: DeviceId, command: BufferType, endpoint: MsgId.Endpoint = MsgId.Endpoint.AppDefaultEndpoint, fit_buf: bool = False):
        if fit_buf:
            command = fit_buffer(command, deviceid.cls.get_size(endpoint), 0x00)
        else:
            command_len = len(command)
            print(deviceid, deviceid.cls, type(deviceid.cls))
            expected_command_len = deviceid.cls.get_size(endpoint)

            if command_len != expected_command_len:
                raise Exception(f"invalid data size ({command_len}) for "
                                f"the DataType {deviceid.cls.name} ({expected_command_len})")

        super(Command, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.Command,
                query_type=MsgId.QueryType.Query,
                device_id=deviceid,
                endpoint=endpoint,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=command
        )


# TODO add reset (soft, WDT, hard, ...) commands,
class BoardLevelCommand(CaniotMessage):
    def __init__(self, deviceid: DeviceId, coc1: XPS, coc2: XPS, crl1: XPS, crl2: XPS = XPS.SET_NONE,
                 HR: bool = False, SR: bool = False, WR: bool = False, WDT: int = 0):
        command = [
            coc1 | (coc2 << 3) | ((crl1 & 0b11) << 6),
            ((crl1 >> 2) & 1) | (crl2 << 1),
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        super(BoardLevelCommand, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.Command,
                query_type=MsgId.QueryType.Query,
                device_id=deviceid,
                endpoint=MsgId.Endpoint.BoardControlEndpoint,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=command
        )

class QueryTelemetry(CaniotMessage):
    def __init__(self, deviceid: DeviceId, endpoint: MsgId.Endpoint = MsgId.Endpoint.AppDefaultEndpoint):
        super(QueryTelemetry, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.Telemetry,
                query_type=MsgId.QueryType.Query,
                endpoint=endpoint,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            )
        )
