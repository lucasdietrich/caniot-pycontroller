from abc import ABC

from .message import CaniotMessage
from cancontroller.caniot.models import MsgId
from cancontroller.caniot.models import BufferType

import struct

class AttributeResponse(CaniotMessage):
    def get_key(self) -> int:
        return self.parse()[0]

    def get_value(self) -> int:
        return self.parse()[1]

    def parse(self) -> (int, int):
        """
        Return ReadAttribute/WriteAttribute response

        Returns: key, attribute value
        """
        return struct.unpack("<HL", bytearray(self.buffer))


class TelemetryMessage(CaniotMessage):
    def match(self, device) -> bool:
        return len(self.buffer) == device.deviceid.data_type.get_size()

    # def explain(self, device: Device) -> dict:
    #     return device.explain_telemetry(self)