import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *

from enum import IntEnum, auto

from cancontroller.caniot.misc import read_bit

import model_pb2

# inherit grpc proto per Device type


class GarageDoorController(Device):
    telemetry = {
        "in0": None,
        "in1": None,
        "in2": None,
        "in3": None,
        "temp0": 0.0,
        "analog0": 0,
        "analog1": 0,
        "analog2": 0,
    }


    class Door(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2
        BOTH = 3

    def open_door(self, door: Door.BOTH) -> Command:
        return Command(self.deviceid, [0, door], fit_buf=True)

    def tcn75_raw2float(self, raw: bytes) -> float:
        return struct.unpack("h", raw)[0] / 100.0

    def interpret(self, msg: CaniotMessage) -> bool:
        super(GarageDoorController, self).interpret(msg)

        for bit in range(4):
            self.telemetry[f"in{bit}"] = read_bit(msg.buffer[0], bit)

        self.telemetry["temp0"] = self.tcn75_raw2float(bytearray(msg.buffer[2:4]))

        return True

    def model(self) -> dict:
        return {
            "garage": model_pb2.GarageDoorModel(**self.telemetry)
        }
