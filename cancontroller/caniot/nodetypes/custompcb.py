import copy
import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.models import DeviceId
from cancontroller.utils import extract_bits_from_bytearray
from cancontroller.caniot.datatypes import *

import model_pb2

class CustomPcb_Node(Device):
    def interpret_board_control_telemetry(self, msg: CaniotMessage) -> dict:
        b0 = msg.buffer[0]
        b1 = msg.buffer[1]

        int_temp = extract_bits_from_bytearray(msg.buffer[2:], 0, 10)
        ext_temp = extract_bits_from_bytearray(msg.buffer[2:], 10, 10)

        self.model["base"].update({
            "r1": bool(b0 & (1 << 0)),
            "r2": bool(b0 & (1 << 2)),
            "oc1": bool(b0 & (1 << 4)),
            "oc2": bool(b0 & (1 << 6)),
            "in1": bool(b1 & (1 << 0)),
            "in2": bool(b1 & (1 << 2)),
            "in3": bool(b1 & (1 << 4)),
            "in4": bool(b1 & (1 << 6)),
            "active_int_temp": IsActiveT10(int_temp),
            "int_temp": IntTemp2float(int_temp),
            "active_ext_temp": IsActiveT10(ext_temp),
            "ext_temp": IntTemp2float(ext_temp),
        })

    def __init__(self, deviceid: DeviceId, name: str = None):
        super(CustomPcb_Node, self).__init__(deviceid, name)

        self.model.update({
            "base": {
                "r1": 0,
                "r2": 0,
                "oc1": 0,
                "oc2": 0,
                "in1": 0,
                "in2": 0,
                "in3": 0,
                "in4": 0,
                "int_temp": 0,
                "active_int_temp": False,
                "ext_temp": 0,
                "active_ext_temp": False,
            }
        })

    def get_model(self) -> dict:
        return {
            "base": model_pb2.CustomPCBModel(**self.model)
        }
