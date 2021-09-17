import asyncio
import datetime
import logging

import can
from grpc import aio

from cancontroller.caniot.message import CaniotMessage, Query, ReadAttributeQuery, WriteAttributeQuery, AttributeResponse
from cancontroller.caniot.models import MsgId, DeviceId
from cancontroller.caniot.device import Device
from cancontroller.controller import initialize_can_if
from cancontroller.ipc import model_pb2_grpc, model_pb2
from pending import PendingQuery, PendingQueriesManager
from cancontroller.controller.devices import Devices
import contextlib
import time

from cancontroller.ipc.model_pb2 import DeviceId as Did

logging.basicConfig()
logging.getLogger("caniot.interfaces.socketcan.socketcan").setLevel(logging.WARNING)
can_logger = logging.getLogger("caniot")
can_logger.setLevel(logging.DEBUG)
grpc_logger = logging.getLogger("grpc")
grpc_logger.setLevel(logging.DEBUG)


class CanController(model_pb2_grpc.CanControllerServicer):
    def __init__(self, bitrate: int = 500000, controller_id: MsgId.Controller = MsgId.Controller.Main):
        self.bitrate = bitrate
        self.controller_id = controller_id
        for can_if in ["can0", "can1"]:
            initialize_can_if(can_if, bitrate=bitrate)

        self.pending_queries_manager = PendingQueriesManager()

        # can1 is actually can0 on the board
        self.can0 = can.Bus(channel='can1', bustype='socketcan')  # , receive_own_messages=True
        # self.reader = can.AsyncBufferedReader()
        logger = can.Logger('logfile.asc')

        # reader = can.AsyncBufferedReader()
        # can.AsyncBufferedReader.get_message()

        listeners = [
            self.recv,
            # self.reader,

            # logger  # Regular Listener object
        ]

        loop = asyncio.get_event_loop()
        self.notifier = can.Notifier(self.can0, listeners, loop=loop)

        self.devices = Devices()

        self.rx_count = 0
        self.tx_count = 0

    def send(self, msg: Query) -> Device:
        can_logger.debug(f"[{self.tx_count}] TX {msg.msgid} payload[{len(msg.buffer)}] : {msg.buffer}")

        self.can0.send(msg.can(), timeout=None)  # define global timeout

        device: Device = self.devices.select(msg.msgid.device_id)
        if device:
            device.pending_query = PendingQuery(msg)
            device.status["sent"] += 1
        else:
            can_logger.warning(f"Sending to an unkown device : {msg.msgid}")

        self.tx_count += 1

        return device

    def recv(self, can_msg: can.Message):
        msg = CaniotMessage(MsgId.from_int(can_msg.arbitration_id, False), can_msg.data)

        can_logger.debug(f"[{self.rx_count}] RX {msg.msgid} payload[{len(msg.buffer)}] : {msg.buffer}")

        device: Device = self.devices.select(msg.msgid.device_id)
        if device:
            device.status["last_seen"] = datetime.datetime.now().isoformat()
            device.status["received"] += 1

            if device.pending_query:
                device.pending_query.response = msg
                device.pending_query.event.set()

        self.rx_count += 1

    async def query(self, msg: Query, timeout: float):
        device: Device = self.send(msg)

        start = time.time()
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(device.pending_query.event.wait(), timeout=timeout)
        duration = time.time() - start

        return device.pending_query.response, duration

    async def SendGarage(self, request: model_pb2.GarageCommand, context) -> model_pb2.GarageResponse:
        self.send(self.devices["GarageDoorControllerProdPCB"].open_door(request.command))
        return model_pb2.GarageResponse(datetime=request.datetime, status="OK")


    async def ReadAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        print(id(request.device.__class__))
        print(id(model_pb2.DeviceId(type=12, id=23).__class__))
        return model_pb2.AttributeResponse(device=request.device, key=1, value=2, status="OK", response_time=0.2)

        # model_pb2.Device(
        #     type=request.device.type,
        #     id=request.device.id
        # )

    async def WriteAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        print(request, request.device, request.device.type)
        # return model_pb2.AttributeResponse(
        #     device=request.device,
        #     key=request.key,
        #     value=0,
        #     status="OK" if 0 else "NOK",
        #     response_time=0
        # )

    async def GetDevices(self, request: model_pb2.Empty, context):
        for i in range(10):
            yield model_pb2.Device(type=1, id=2)


async def serve():
    server = aio.server()
    model_pb2_grpc.add_CanControllerServicer_to_server(CanController(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve())
    loop.close()
