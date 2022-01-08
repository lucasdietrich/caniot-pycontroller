import struct

from cancontroller.caniot.device import Device
from cancontroller.caniot.message import *

import model_pb2

# inherit grpc proto per Device type


class CRTHPT_Node(Device):
    model = {
        "base": {
            "contacts": 0,
            "relays": 0,
            "int_temp": 0.0,
            "humidity": 0.0,
            "pressure": 0.0,
            "ext_temp": 0.0
        }
    }

    def IntHum2float(self, H: int) -> float:
        if H == 0:
            return 0.0
        return (H & 0x3ff)/100.0

    def IntPres2float(self, P: int) -> float:
        if P == 0:
            return 0.0
        return (P & 0x3ff)/100.0 + 950.0

    def IntTemp2float(self, T: int) -> float:
        if T == 0:
            return 0.0
        return (T & 0x3ff)/10.0 - 28.0

    def Temperature2float(self, raw: bytes) -> float:
        T = struct.unpack("h", raw)[0]

        return self.IntTemp2float(T)

    def interpret(self, msg: CaniotMessage) -> bool:
        super(CRTHPT_Node, self).interpret(msg)

        base = self.model["base"]

        base["contacts"] = msg.buffer[0]
        base["relays"] = msg.buffer[1]

        measurements = struct.unpack("Q", bytearray(msg.buffer[2:7] + [0, 0, 0]))[0]
        base["int_temp"] = self.IntTemp2float(measurements)
        base["humidity"] = self.IntHum2float(measurements >> 10)
        base["pressure"] = self.IntPres2float(measurements >> 20)
        base["ext_temp"] = self.IntTemp2float(measurements >> 30)

        return True

    def get_model(self) -> dict:
        return {
            "base": model_pb2.CRTHPT_Model(**self.model)
        }
