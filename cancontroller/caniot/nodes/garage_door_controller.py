from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *

from enum import IntEnum, auto

from cancontroller.caniot.misc import read_bit

# inherit grpc proto per Device type


class GarageDoorController(Device):
    telemetry = {
        "raw": None,
        "in0": None,
        "in1": None,
        "in2": None,
        "in3": None
    }

    class Door(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2
        BOTH = 3

    def open_door(self, door: Door.BOTH) -> Command:
        return Command(self.deviceid, [0, door], fit_buf=True)

    def interpret(self, msg: CaniotMessage) -> bool:
        for bit in range(4):
            self.telemetry[f"in{bit}"] = read_bit(msg.buffer[0], bit)

        return True
