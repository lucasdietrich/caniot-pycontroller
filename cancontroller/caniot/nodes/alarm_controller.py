import copy
import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.models import DeviceId
from cancontroller.caniot.nodetypes import CustomPcb_Node

from enum import IntEnum, auto

from cancontroller.caniot.datatypes import IsActiveT10, IntTemp2float
from cancontroller.utils import extract_bits_from_bytearray, read_bit

import model_pb2

# inherit grpc proto per Device type


class AlarmController(CustomPcb_Node):
    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

    def get_model(self):
        return {
            "alarm": model_pb2.AlarmControllerModel(**self.model)
        }