import abc
import datetime
from enum import IntEnum

from cancontroller.caniot.models import DeviceId, MsgId
from cancontroller.caniot.message import *

from typing import Optional

import json


class Device:
    """
    Represent a caniot device on the can bus.

    Gather all device specific methods

    A device can only have one pending request
    """

    class ResetType(IntEnum):
        HardwareReset = 1 << 0
        SoftwareReset = 1 << 1
        WatchdogReset = 1 << 2

    # class WatchdogCommand
    #     # WatchdogEnable = (1 << 3)
    #     # WatchdogDisable = (2 << 3)

    # last_seen: datetime.datetime = None
    # received = 0
    # sent = 0
    #
    # model = {}
    class AttributesValues:
        def __init__(self):
            self.array = {}

        def __setitem__(self, key, value):
            self.array[key] = value

        def __getitem__(self, item):
            return self.array[item]

        def items(self):
            return self.array.items()

    def __init__(self, deviceid: DeviceId, name: str = None):
        self.telemetry_raw = []
        self.model = {
            "base": {}
        }
        self.attrs = Device.AttributesValues()

        self.last_seen: datetime.datetime = None

        self.received = 0
        self.sent = 0

        self.deviceid: DeviceId = deviceid
        self.name = name
        self.version = 0

    def __repr__(self):
        return f"Device {self.name} {self.deviceid}\n" + self.__dict__.__repr__()

    def reset(self, rtype: ResetType = ResetType.HardwareReset) -> Command:
        return Command(self.deviceid, [rtype], MsgId.Endpoint.BoardControlEndpoint, fit_buf=True)

    def query(self) -> QueryTelemetry:
        return QueryTelemetry(self.deviceid)

    def read_attribute(self, key: int) -> ReadAttributeQuery:
        return ReadAttributeQuery(self.deviceid, key)

    def write_attribute(self, key: int, value: int) -> WriteAttributeQuery:
        return WriteAttributeQuery(self.deviceid, key, value)

    def query_telemetry(self) -> QueryTelemetry:
        return QueryTelemetry(self.deviceid)

    def set_time(self, utc: int) -> WriteAttributeQuery:
        return WriteAttributeQuery(self.deviceid, 0x1010, utc)

    def handle(self, msg: CaniotMessage) -> Optional[CaniotMessage]:
        if isinstance(msg, AttributeResponse):
            self.attrs[msg.get_key()] = msg.get_value()
        elif isinstance(msg, TelemetryMessage):
            return self.handle_telemetry(msg)
        else:
            raise Exception(f"Cannot interpret CANIOT response {msg}")

    @abc.abstractmethod
    def handle_board_control_telemetry(self, msg: CaniotMessage) -> Optional[CaniotMessage]:
        raise NotImplemented

    @abc.abstractmethod
    def handle_application_telemetry(self, msg: CaniotMessage) -> Optional[CaniotMessage]:
        raise NotImplemented

    def handle_telemetry(self, msg: CaniotMessage):
        if msg.msgid.endpoint == MsgId.Endpoint.BoardControlEndpoint:
            assert len(msg.buffer) == 8
            return self.handle_board_control_telemetry(msg)
        else:
            return self.handle_application_telemetry(msg)

    def get_model(self) -> dict:
        return {}

    def json(self) -> str:
        return json.dumps(self.get_model())