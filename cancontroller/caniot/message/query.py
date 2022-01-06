from abc import ABC

from .message import CaniotMessage
from cancontroller.caniot.models import BufferType, MsgId, DeviceId
from cancontroller.caniot.misc import fit_buffer

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
    def __init__(self, deviceid: DeviceId, command: BufferType, endpoint: MsgId.Endpoint = MsgId.Endpoint.Default, fit_buf: bool = False):
        if fit_buf:
            command = fit_buffer(command, deviceid.cls.get_size(), 0x00)
        else:
            command_len = len(command)
            expected_command_len = deviceid.cls.get_size()

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


class QueryTelemetry(CaniotMessage):
    def __init__(self, deviceid: DeviceId, endpoint: MsgId.Endpoint = MsgId.Endpoint.Default):
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
