import copy
import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.models import DeviceId
from cancontroller.utils import extract_bits_from_bytearray, read_bit
from cancontroller.caniot.datatypes import *

import model_pb2

class CustomPcb_Node(Device):
    def command(self, coc1: XPS = XPS.SET_NONE, coc2: XPS = XPS.SET_NONE,
                crl1: XPS = XPS.SET_NONE, crl2: XPS = XPS.SET_NONE):
        return BoardLevelCommand(self.deviceid, coc1, coc2, crl1, crl2)

    def interpret_application_telemetry(self, msg: CaniotMessage):
        pass

    def interpret_board_control_telemetry(self, msg: CaniotMessage):
        b0 = msg.buffer[0]
        b1 = msg.buffer[1]

        int_temp = extract_bits_from_bytearray(msg.buffer[2:], 0, 10)
        ext_temp = extract_bits_from_bytearray(msg.buffer[2:], 10, 10)

        self.model["base"].update({
            "oc1": read_bit(b0, 0),
            "oc2": read_bit(b0, 1),
            "rl1": read_bit(b0, 2),
            "rl2": read_bit(b0, 3),
            "in1": read_bit(b0, 4),
            "in2": read_bit(b0, 5),
            "in3": read_bit(b0, 6),
            "in4": read_bit(b0, 7),
            "poc1": read_bit(b1, 0),
            "poc2": read_bit(b1, 1),
            "prl1": read_bit(b1, 2),
            "prl2": read_bit(b1, 3),
            "active_int_temp": IsActiveT10(int_temp),
            "int_temp": IntTemp2float(int_temp),
            "active_ext_temp": IsActiveT10(ext_temp),
            "ext_temp": IntTemp2float(ext_temp),
        })

    def __init__(self, deviceid: DeviceId, name: str = None):
        super(CustomPcb_Node, self).__init__(deviceid, name)

        self.model.update({
            "base": {
                "oc1": 0,
                "oc2": 0,
                "rl1": 0,
                "rl2": 0,
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