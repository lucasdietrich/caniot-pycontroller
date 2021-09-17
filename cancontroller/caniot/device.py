from cancontroller.caniot.models import DeviceId, MsgId
from cancontroller.caniot.message import *
from cancontroller.controller.pending import PendingQuery


class Device:
    """
    Represent a caniot device on the can bus.

    Gather all device specific methods

    A device can only have one pending request
    """

    pending_query: PendingQuery = None
    status = {
        "last_seen": None,
        "received": 0,
        "sent": 0,
    }

    def __init__(self, deviceid: DeviceId):
        self.deviceid = deviceid

    def __repr__(self):
        return f"Device {self.deviceid}"

    # def address(self, from_controller: MsgId.Controller):
    #     pass

    def query(self, buffer: list) -> QueryTelemetry:
        return QueryTelemetry(self)

    def read_attribute(self, key: int) -> ReadAttributeQuery:
        return ReadAttributeQuery(self, key)

    def query_telemetry(self) -> QueryTelemetry:
        return QueryTelemetry(self)

    def set_time(self, utc: int) -> WriteAttributeQuery:
        return WriteAttributeQuery(self, 0x1010, utc)
