import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.nodetypes import CRTHPT_Node

from enum import IntEnum, auto

from cancontroller.caniot.misc import read_bit

import model_pb2

# inherit grpc proto per Device type


class AlarmController(CRTHPT_Node):
    model = {**CRTHPT_Node.model, **{
        "light1": 0,
        "light2": 0,
        "alarm": 0, # alarm state
    }}

    def interpret(self, msg: CaniotMessage) -> bool:
        super(AlarmController, self).interpret(msg)

        self.model["light1"] = read_bit(msg.buffer[0], 0)
        self.model["light2"] = read_bit(msg.buffer[0], 1)

        self.model["alarm"] = (msg.buffer[0] >> 2) & 0x3

        return True

    def command(self, light1: int, light2: int, alarm: int) -> Command:
        return Command(self.deviceid, [0, light1 | (light2 << 2) | (alarm << 4)], fit_buf=True)

    def get_model(self) -> dict:
        return {
            "alarm": model_pb2.AlarmControllerModel(**self.model)
        }
