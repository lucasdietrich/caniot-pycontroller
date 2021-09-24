import abc

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
    status = {
        "last_seen": None,
        "received": 0,
        "sent": 0,
    }

    telemetry = {
        "raw": []
    }

    def __init__(self, deviceid: DeviceId, name: str = None):
        self.deviceid = deviceid
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

    def interpret(self, msg: CaniotMessage) -> bool:
        self.telemetry["raw"] = msg.buffer
        return True

    def model(self) -> dict:
        return {}

    def json(self) -> str:
        return json.dumps(self.model())