import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.nodetypes import CRTHPT_Node

from enum import IntEnum, auto

from cancontroller.caniot.misc import read_bit

import model_pb2

# inherit grpc proto per Device type


class GarageDoorController(CRTHPT_Node):
    model = {**CRTHPT_Node.model, **{
        "left": 1,
        "right": 1,
        "gate": 1,
    }}

    class Door(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2
        BOTH = 3

    def open_door(self, door: Door.BOTH) -> Command:
        return Command(self.deviceid, [0, door], fit_buf=True)

    def interpret(self, msg: CaniotMessage) -> bool:
        super(GarageDoorController, self).interpret(msg)

        self.model["left"] = read_bit(msg.buffer[0], 0)
        self.model["right"] = read_bit(msg.buffer[0], 1)
        self.model["gate"] = read_bit(msg.buffer[0], 2)

        return True

    def get_model(self):
        return {
            "garage": model_pb2.GarageDoorModel(**self.model)
        }
