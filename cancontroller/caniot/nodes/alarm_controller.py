import copy
import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *
from cancontroller.caniot.models import DeviceId
from cancontroller.caniot.nodetypes import CRTHPT_Node

from enum import IntEnum, auto

from cancontroller.caniot.misc import read_bit

import model_pb2

# inherit grpc proto per Device type


class AlarmController(CRTHPT_Node):
    def __init__(self, deviceid: DeviceId, name: str = None):
        super().__init__(deviceid, name)

        self.model.update({
            "light1": 0,
            "light2": 0,
            "state": 0,  # alarm state
            "mode": 0,  # alarm mode
        })

    def interpret_telemetry(self, msg: CaniotMessage) -> bool:
        super(AlarmController, self).interpret_telemetry(msg)

        self.model["light1"] = read_bit(msg.buffer[0], 0)
        self.model["light2"] = read_bit(msg.buffer[0], 1)
        self.model["siren"] = read_bit(msg.buffer[0], 5)

        self.model["state"] = (msg.buffer[0] >> 2) & 0x3
        self.model["mode"] = (msg.buffer[0] >> 4) & 0x1

        return True

    def command(self, light1: int, light2: int, alarm: int, alarm_mode: int, siren: int) -> Command:
        return Command(self.deviceid, [(siren << 6), light1 | (light2 << 2) | (alarm << 4) | (alarm_mode << 6)], fit_buf=True)

    def get_model(self) -> dict:
        return {
            "alarm": model_pb2.AlarmControllerModel(**self.model)
        }
