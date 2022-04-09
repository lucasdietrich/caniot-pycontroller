import copy
import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.nodetypes import CustomPcb_Node
from cancontroller.caniot.models import DeviceId
from cancontroller.utils import extract_bits_from_bytearray
from cancontroller.caniot.datatypes import *

from enum import IntEnum, auto

from cancontroller.utils import read_bit

import model_pb2

# inherit grpc proto per Device type


class GarageDoorController(CustomPcb_Node):
    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

        self.model.update({
            "left": 1,
            "right": 1,
            "gate": 1,
        })

    def open_door(self, door) -> Command:
        params = dict()

        if door == model_pb2.COMMAND_LEFT or door == model_pb2.COMMAND_ALL:
            params["crl1"] = XPS.PULSE_ON

        if door == model_pb2.COMMAND_RIGHT or door == model_pb2.COMMAND_ALL:
            params["crl2"] = XPS.PULSE_ON

        return self.command(**params)

    def interpret_board_control_telemetry(self, msg: CaniotMessage):
        super(GarageDoorController, self).interpret_board_control_telemetry(msg)

        self.model["left"] = self.model["base"]["in3"]
        self.model["right"] = self.model["base"]["in4"]
        self.model["gate"] = self.model["base"]["in2"]

    def get_model(self):
        return {
            "garage": model_pb2.GarageDoorModel(**self.model)
        }