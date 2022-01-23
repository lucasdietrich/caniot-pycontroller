import abc
import datetime

from cancontroller.caniot.models import DeviceId, MsgId
from cancontroller.caniot.message import *
from cancontroller.controller.pending import PendingQuery

import json


class Device:
    """
    Represent a caniot device on the can bus.

    Gather all device specific methods

    A device can only have one pending request
    """

    # last_seen: datetime.datetime = None
    # received = 0
    # sent = 0
    #
    # telemetry_raw = []
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
        self.model = {}
        self.attrs = Device.AttributesValues()

        self.last_seen: datetime.datetime = None

        self.received = 0
        self.sent = 0

        self.deviceid: DeviceId = deviceid
        self.name = name
        self.version = 0

    def __repr__(self):
        return f"Device {self.name} {self.deviceid}\n" + self.__dict__.__repr__()

    # def address(self, from_controller: MsgId.Controller):
    #     pass

    def query(self, buffer: list) -> QueryTelemetry:
        return QueryTelemetry(self.deviceid)

    def read_attribute(self, key: int) -> ReadAttributeQuery:
        return ReadAttributeQuery(self.deviceid, key)

    def write_attribute(self, key: int, value: int) -> WriteAttributeQuery:
        return WriteAttributeQuery(self.deviceid, key, value)

    def query_telemetry(self) -> QueryTelemetry:
        return QueryTelemetry(self.deviceid)

    def set_time(self, utc: int) -> WriteAttributeQuery:
        return WriteAttributeQuery(self.deviceid, 0x1010, utc)

    def interpret(self, msg: CaniotMessage):
        if isinstance(msg, AttributeResponse):
            self.attrs[msg.get_key()] = msg.get_value()
        elif isinstance(msg, TelemetryMessage):
            self.interpret_telemetry(msg)
        else:
            raise Exception(f"Cannot interpret CANIOT response {msg}")

    def interpret_telemetry(self, msg: CaniotMessage):
        self.telemetry_raw = msg.buffer

    def get_model(self) -> dict:
        return {}

    def json(self) -> str:
        return json.dumps(self.get_model())