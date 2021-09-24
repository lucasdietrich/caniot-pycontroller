from abc import ABC

from .message import CaniotMessage
from cancontroller.caniot.models import BufferType, MsgId, DeviceId
from cancontroller.caniot.misc import fit_buffer

import struct


class Query(CaniotMessage, ABC):
    def set_controller(self, controller: MsgId.Controller = MsgId.Controller.Main):
        self.msgid.controller = controller


class ReadAttributeQuery(Query):
    def __init__(self, deviceid: DeviceId, key: int, controller: MsgId.Controller = MsgId.Controller.Main):
        super(ReadAttributeQuery, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.ReadAttribute,
                query_type=MsgId.QueryType.Query,
                controller=controller,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=struct.pack("<H", key & 0xFFFF)
        )


class WriteAttributeQuery(Query):
    def __init__(self, deviceid: DeviceId, key: int, value: int, controller: MsgId.Controller = MsgId.Controller.Main):
        super(WriteAttributeQuery, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.WriteAttribute,
                query_type=MsgId.QueryType.Query,
                controller=controller,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=struct.pack("<HL", key & 0xFFFF, value & 0xFFFFFFFF)
        )


class Command(Query):
    def __init__(self, deviceid: DeviceId, command: BufferType, controller: MsgId.Controller = MsgId.Controller.Main, fit_buf: bool = False):
        if fit_buf:
            command = fit_buffer(command, deviceid.data_type.get_size(), 0x00)
        else:
            command_len = len(command)
            expected_command_len = deviceid.data_type.get_size()

            if command_len != expected_command_len:
                raise Exception(f"invalid data size ({command_len}) for "
                                f"the DataType {deviceid.data_type.name} ({expected_command_len})")

        super(Command, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.Command,
                query_type=MsgId.QueryType.Query,
                controller=controller,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            ),
            buffer=command
        )


class QueryTelemetry(Query):
    def __init__(self, deviceid: DeviceId, controller: MsgId.Controller = MsgId.Controller.Main):
        super(QueryTelemetry, self).__init__(
            msgid=MsgId(
                frame_type=MsgId.FrameType.Telemetry,
                query_type=MsgId.QueryType.Query,
                controller=controller,
                device_id=deviceid,
                extended_id=0,
                id_type=MsgId.IdType.Standard
            )
        )
