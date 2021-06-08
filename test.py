import time
import random

import struct

import can

import datetime;

from cancontroller.can import initialize_can_if, generate_random_data
from cancontroller import MsgId, DeviceId, DEVICE_BROADCAST

BITRATE = 500000

can_ifs = [
    "can0",
    "can1"
]

msgs = [
    MsgId(
        frame_type=MsgId.FrameType.WriteAttribute,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.Controller1,
        device_id=DeviceId(DeviceId.DataType.CRT, 1)
    ),
    MsgId(
        frame_type=MsgId.FrameType.WriteAttribute,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.Controller1,
        device_id=DeviceId(DeviceId.DataType.CRT, 0)
    ),
    MsgId(
        frame_type=MsgId.FrameType.WriteAttribute,
        query_type=MsgId.QueryType.Query,
        controller=MsgId.Controller.Controller1,
        device_id=DEVICE_BROADCAST
    )
]

# send_msg = can.Message(
#     arbitration_id=int(msgs[i % 3]),
#     data=generate_random_data(8),
#     is_extended_id=False,
#     timestamp=datetime.datetime.now().timestamp()
# )

if __name__ == "__main__":

    for can_if in can_ifs:
        initialize_can_if(can_if, BITRATE)

    canb = can.interface.Bus(channel=can_ifs[1], bustype='socketcan')

    i = 0

    while True:

        try:
            timestamp = datetime.datetime.now().timestamp()
            timestamp_sec = int(timestamp)

            timestamp_sec_uint32_t = struct.pack("<L", timestamp_sec)

            key = struct.pack("h", 0x0101)

            write_datetime = can.Message(
                arbitration_id=int(MsgId(
                    frame_type=MsgId.FrameType.WriteAttribute,
                    query_type=MsgId.QueryType.Query,
                    controller=MsgId.Controller.Controller1,
                    device_id=DeviceId(DeviceId.DataType.CRT, 0)
                )),
                data=key + timestamp_sec_uint32_t,
                is_extended_id=False,
                timestamp=timestamp
            )
            

            canb.send(write_datetime)
            print(f"can message sent on \t{canb.channel_info} : {write_datetime}")
        except can.CanError:
            print("can message NOT sent : {msg}")

        

        while True:
            recv_msg = canb.recv(timeout=1.0)

            if recv_msg:
                print(f"can message received on {canb.channel_info} : {recv_msg}")
            else:
                break

        time.sleep(5.0)
