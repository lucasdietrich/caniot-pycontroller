import asyncio
import datetime
import logging

import can
from grpc import aio

from cancontroller.caniot.message import CaniotMessage, Query, AttributeResponse
from cancontroller.caniot.message.interpret import interpret_response
from cancontroller.caniot.models import MsgId, DeviceId
from cancontroller.caniot.device import Device
from cancontroller.controller import initialize_can_if

from typing import List

import model_pb2_grpc, model_pb2
from pending import PendingQuery
from cancontroller.caniot.devices import Devices
import contextlib
import time

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
        self.pending: List[PendingQuery] = []

        self.rx_count = 0
        self.tx_count = 0

    def send(self, msg: Query) -> Device:
        can_logger.debug(f"[{self.tx_count}] TX {msg.msgid} payload[{len(msg.buffer)}] : {msg.buffer}")

        self.can0.send(msg.can(), timeout=None)  # define global timeout

        device: Device = self.devices.select(msg.msgid.device_id)
        if device:
            device.sent += 1
        else:
            can_logger.warning(f"Sending to an unkown device : {msg.msgid}")

        self.tx_count += 1

        return device

    def recv(self, can_msg: can.Message):
        # interpret as caniot message
        msg = interpret_response(MsgId.from_int(can_msg.arbitration_id, False), can_msg.data)

        can_logger.debug(f"[{self.rx_count}] RX {msg.msgid} payload[{len(msg.buffer)}] : {msg.buffer}")

        # update device table
        device: Device = self.devices.select(msg.msgid.device_id)
        if device:
            device.last_seen = datetime.datetime.now()
            device.received += 1
            device.interpret(msg)

        for query in self.pending:
            if query.eval(msg):
                break

        self.rx_count += 1

    async def query(self, msg: Query, timeout: float) -> [CaniotMessage, float]:
        pending_query = PendingQuery(query=msg)
        self.pending.append(pending_query)

        self.send(msg)

        start = time.time()
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(pending_query.event.wait(), timeout=timeout)
        duration = time.time() - start

        responses = pending_query.responses
        self.pending.remove(pending_query)

        return responses, duration

    async def SendGarage(self, request: model_pb2.GarageCommand, context) -> model_pb2.GarageResponse:
        query = self.devices["GarageDoorControllerProdPCB"].open_door(request.command)
        self.send(query)
        return model_pb2.GarageResponse(datetime=request.datetime, status="OK")

    async def QueryAttribute(self, query: Query, timeout: float):
        response, duration = await self.query(query, timeout)
        attr_response: AttributeResponse = response[0]
        return model_pb2.AttributeResponse(device=model_pb2.DeviceId(
            type=attr_response.msgid.device_id.data_type,
            id=attr_response.msgid.device_id.sub_id
        ), key=attr_response.get_key(), value=attr_response.get_value(), status="OK" if response else "TIMEOUT",
            response_time=duration)

    async def ReadAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        query = Device(DeviceId(data_type=request.device.type, sub_id=request.device.id)).read_attribute(request.key)
        return await self.QueryAttribute(query, request.timeout)

    async def WriteAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        query = Device(DeviceId(data_type=request.device.type, sub_id=request.device.id)).write_attribute(request.key, request.value)
        return await self.QueryAttribute(query, request.timeout)

    async def GetDevices(self, request: model_pb2.Empty, context):
        return model_pb2.Devices(device=[
            model_pb2.Device() for dev in self.devices.devices
        ])

    # allow this method to be blocking until timeout
    async def RequestTelemetry(self, request: model_pb2.DeviceId, context):
        self.send(Device(DeviceId(data_type=request.type, sub_id=request.id)).query_telemetry())
        return model_pb2.Empty()

    async def GetDevice(self, request: model_pb2.Devices, context):
        dev: Device = self.devices.select(DeviceId(request.type, request.id))
        if dev:
            return model_pb2.Device(
                deviceid=request,
                name=dev.name,
                version=dev.version,
                status=model_pb2.Device.Status(
                    last_seen=model_pb2.DateTime(
                        iso=dev.last_seen.isoformat(),
                        formatted=dev.last_seen.strftime("%Y-%m-%d %H:%M:%S"),
                        year=dev.last_seen.year,
                        month=dev.last_seen.month,
                        day=dev.last_seen.day,
                        hour=dev.last_seen.hour,
                        minute=dev.last_seen.minute,
                        second=dev.last_seen.second
                    ) if dev.last_seen else None,
                    received=dev.received,
                    sent=dev.sent,
                    online=bool(dev.last_seen)
                ),
                raw=dev.telemetry_raw,
                **dev.model()
            )
        else:
            return model_pb2.Empty()


async def serve():
    server = aio.server()
    model_pb2_grpc.add_CanControllerServicer_to_server(CanController(), server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    # TODO server.add_secure_port()
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve())
    loop.close()
