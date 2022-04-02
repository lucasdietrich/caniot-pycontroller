import copy
import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.nodetypes import CustomPcb_Node
from cancontroller.caniot.models import DeviceId
from cancontroller.utils import extract_bits_from_bytearray
from cancontroller.caniot.datatypes import *

from enum import IntEnum, auto

from cancontroller.caniot.misc import read_bit

import model_pb2

# inherit grpc proto per Device type


class GarageDoorController(CustomPcb_Node):
    class Door(IntEnum):
        NONE = 0
        LEFT = 1
        RIGHT = 2
        BOTH = 3

    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

        self.model.update({
            "left": 1,
            "right": 1,
            "gate": 1,
        })

    def open_door(self, door: Door.BOTH) -> Command:
        return Command(self.deviceid, [0, door], fit_buf=True)

    def interpret_application_telemetry(self, msg: CaniotMessage) -> bool:
        self.model["left"] = read_bit(msg.buffer[0], 0)
        self.model["right"] = read_bit(msg.buffer[0], 1)
        self.model["gate"] = read_bit(msg.buffer[0], 2)

        int_temp = extract_bits_from_bytearray(msg.buffer[2:], 0, 10)

        self.model["base"].update({
            "active_ext_temp": False,
            "ext_temp": U10_MAX_VALUE,
            "active_int_temp": IsActiveT10(int_temp),
            "int_temp": IntTemp2float(int_temp)
        })

        return True

    def get_model(self):
        return {
            "garage": model_pb2.GarageDoorModel(**self.model)
        }
