import asyncio
import can

from cancontroller.controller import initialize_can_if


def print_message(msg):
    print(msg)


async def main():
    for can_if in ["can0", "can1"]:
        initialize_can_if(can_if, bitrate=500000)

    can0 = can.Bus('can1', bustype='socketcan', receive_own_messages=True)
    reader = can.AsyncBufferedReader()
    logger = can.Logger('logfile.asc')

    listeners = [
        print_message,  # Callback function
        reader,         # AsyncBufferedReader() listener
        logger          # Regular Listener object
    ]

    loop = asyncio.get_event_loop()
    notifier = can.Notifier(can0, listeners, loop=loop)

    # can0.send(can.Message(arbitration_id=0))
    while True:
        try:
            msg = await reader.get_message()

        except:
            break

    # Clean-up
    notifier.stop()
    can0.shutdown()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()