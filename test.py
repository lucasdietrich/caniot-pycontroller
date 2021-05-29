import time
import random

import can

from cancontroller.can import initialize_can_if, generate_random_data

BITRATE = 500000

can_ifs = [
    "can0",
    "can1"
]

if __name__ == "__main__":

    for can_if in can_ifs:
        initialize_can_if(can_if, BITRATE)

    canb = can.interface.Bus(channel=can_ifs[1], bustype='socketcan')

    while True:

        send_msg = can.Message(arbitration_id=0xA0FFEE,
                      data=generate_random_data(8),
                      is_extended_id=True)

        try:
            canb.send(send_msg)
            print(f"can message sent on \t{canb.channel_info} : {send_msg}")
        except can.CanError:
            print("can message NOT sent : {msg}")

        while True:
            recv_msg = canb.recv(timeout=1.0)

            if recv_msg:
                print(f"can message received on {canb.channel_info} : {recv_msg}")
            else:
                break

        time.sleep(1.0)