import asyncio
import logging

import can
from grpc import aio

from cancontroller.controller import initialize_can_if
from cancontroller.controller.models import send_garage_can_command
from cancontroller.ipc import model_pb2_grpc, model_pb2


class CanController(model_pb2_grpc.CanControllerServicer):
    def __init__(self):
        for can_if in ["can0", "can1"]:
            initialize_can_if(can_if, bitrate=500000)

        self.can0 = can.Bus('can1', bustype='socketcan', receive_own_messages=True)
        self.reader = can.AsyncBufferedReader()
        logger = can.Logger('logfile.asc')

        listeners = [
            self.print_can_message,  # Callback function
            self.reader,  # AsyncBufferedReader() listener
            self.handle_can_message,
            logger  # Regular Listener object
        ]

        loop = asyncio.get_event_loop()
        self.notifier = can.Notifier(self.can0, listeners, loop=loop)

    async def run(self):
        # can0.send(can.Message(arbitration_id=0))
        while True:
            try:
                msg = await self.reader.get_message()

            except:
                break

        # Clean-up
        self.notifier.stop()
        self.can0.shutdown()

    def SendGarage(self, request, context):
        print(f"GarageResponse command={request.command}")
        self.can0.send(send_garage_can_command(request.command))
        return model_pb2.GarageResponse(datetime=request.datetime, status="NOK")

    def print_can_message(self, msg):
        print(msg)

    def handle_can_message(self, msg: can.Message):
        print("handle_can_message")


async def serve():
    server = aio.server()
    model_pb2_grpc.add_CanControllerServicer_to_server(CanController(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # asyncio.run(serve())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve())
    loop.close()