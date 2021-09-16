import struct

from cancontroller.controller.interface import initialize_can_if
import can

import datetime

from cancontroller.caniot.models import MsgId, DeviceId, ControllerMessageBuilder

initialize_can_if("can1")

can0 = can.Bus(channel='can1', bustype='socketcan')

device = DeviceId(DeviceId.DataType.CRT, 1)


def _attr(key: int = 0x1010, value: int = None, write: bool = False):
    if write:
        if value is None:
            value = int(datetime.datetime.now().timestamp())

        msgid, query = ControllerMessageBuilder().WriteAttribute(device, key, value)  # write device id
    else:
        msgid, query = ControllerMessageBuilder().ReadAttribute(device, key)  # read device id

    print(f"TX {msgid} : {query.data}")
    can0.send(query)

    msg: can.Message = can0.recv(timeout=1.0)
    msgid = MsgId.from_int(msg.arbitration_id)
    if msg and len(msg.data) == 6:
        print(f"RX {msgid} : {msg.data}")

        return struct.unpack("<L", msg.data[2:6])[0]
    elif msgid.is_error():
        print(f"{msgid}")
    else:
        print("payload size problem or other ? ...")


def read_attr(key: int = 0x0000):
    return _attr(key)


def write_attr(key: int = 0x1010, value: int = None):
    return _attr(key, value, True)


def read_system():
    for attr in range(16):
        read_attr(0x1000 | attr << 4)


def read_identification():
    for attr in range(3):

        if attr == 2:
            for part in range(8):
                read_attr(attr << 4 | part)
        else:
            read_attr(attr << 4)


if __name__ == "__main__":
    read_attr()
