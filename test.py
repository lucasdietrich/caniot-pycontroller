import time
import random

import struct

import can

import datetime

from cancontroller.controller import initialize_can_if, generate_random_data
from cancontroller import MsgId, DEVICE_BROADCAST

BITRATE = 500000

can_ifs = [
    "can0",
    "can1"
]


def write_datetime() -> can.Message:
    timestamp = datetime.datetime.now().timestamp()
    timestamp_sec = int(timestamp)

    timestamp_sec_uint32_t = struct.pack("<L", timestamp_sec)

    key = struct.pack("h", 0x0101)

    return can.Message(
        arbitration_id=int(MsgId(
            frame_type=MsgId.FrameType.WriteAttribute,
            query_type=MsgId.QueryType.Query,
            controller=MsgId.Controller.Controller1,
            data_type=MsgId.DataType.CRT,
            device_id=0
        )),
        data=key + timestamp_sec_uint32_t,
        is_extended_id=False,
        timestamp=timestamp
    )


def send(msg : can.Message) -> bool:
    try:
        canb.send(msg)
        print(f"CAN send {MsgId.from_raw(msg.arbitration_id)} : {msg.data}")
    except can.CanError:
        print("controller message NOT sent : {msg}")
        return False
    
    return True


if __name__ == "__main__":

    for can_if in can_ifs:
        initialize_can_if(can_if, BITRATE)

    canb = can.interface.Bus(channel=can_ifs[1], bustype='socketcan')

    send(write_datetime())

    while True:
        msg: can.Message = canb.recv(timeout=1.0)

        if msg:
            print(f"CAN recv [{hex(msg.arbitration_id)[2:]}] : {MsgId.from_raw(msg.arbitration_id)} : {msg.data}")
