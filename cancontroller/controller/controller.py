import asyncio
import datetime
import logging

import can
from grpc import aio
import os.path

from cancontroller import configuration, ROOT_DIR
from cancontroller.caniot.message.interpret import interpret_response
from cancontroller.controller import initialize_can_if

from cancontroller.caniot import *

from typing import List

import model_pb2, model_pb2_grpc
from pending import PendingQuery
from cancontroller.controller.devices import Devices, node_garage_door, devices, node_alarm
import contextlib
import time

logging.basicConfig()
logging.getLogger("caniot.interfaces.socketcan.socketcan").setLevel(logging.DEBUG)

can_logger = logging.getLogger("caniot")
can_logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(configuration.get_controller_log_file())
formatter = logging.Formatter('caniot: %(asctime)s - %(name)s - %(levelname)s - %(message)s')
fileHandler.setFormatter(formatter)
can_logger.addHandler(fileHandler)


class CanController(model_pb2_grpc.CanControllerServicer):
    def __init__(self, bitrate: int = configuration.can_bus_speed):
        self.bitrate = bitrate
        for can_if in ["can0", "can1"]:
            initialize_can_if(can_if, bitrate=bitrate)

        # can1 is actually can0 on the board
        self.can0 = can.Bus(channel=configuration.can_bus, bustype='socketcan')

        # self.reader = can.AsyncBufferedReader()
        logger = can.Logger(os.path.join(ROOT_DIR, configuration.get_can_log_file()))

        # reader = can.AsyncBufferedReader()
        # can.AsyncBufferedReader.get_message()

        # self.can0.set_filters()

        loop = asyncio.get_event_loop()
        self.notifier = can.Notifier(self.can0, [
            self.recv,
            logger
        ], loop=loop)

        self.devices = Devices()
        self.pending: List[PendingQuery] = []

        self.rx_count = 0
        self.tx_count = 0

    async def send(self, msg: CaniotMessage) -> Device:
        can_logger.debug(f"[{self.tx_count}] TX {msg.msgid} payload[{len(msg.buffer)}] : {msg.buffer}")

        self.can0.send(msg.can(), timeout=None)  # define global timeout

        device: Device = self.devices.select(msg.msgid.device_id)
        if device:
            device.sent += 1
        elif not msg.msgid.is_broadcast_device():
            can_logger.warning(f"Sending to an unknown device : {msg.msgid}")

        self.tx_count += 1

        return device

    async def recv(self, can_msg: can.Message):
        # interpret as caniot message
        msg = interpret_response(MsgId.from_int(can_msg.arbitration_id, False), can_msg.data)

        log_msg = str(msg)

        self.rx_count += 1

        if msg.msgid.is_response():
            # update device table
            device: Device = self.devices.select(msg.msgid.device_id)
            if device:
                device.last_seen = datetime.datetime.now()
                device.received += 1

                req = device.handle(msg)
                if req is not None:
                   await self.query(req)

                log_msg += " " + str(device.model)

            for query in self.pending:
                if query.eval(msg):
                    break

        if msg.msgid.is_error():
            can_logger.error(log_msg)
        else:
            can_logger.debug(log_msg)

    async def query(self, msg: CaniotMessage, timeout: float = 0.0) -> [CaniotMessage, float]:
        pending_query = PendingQuery(query=msg)
        self.pending.append(pending_query)

        await self.send(msg)

        start = time.time()
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(pending_query.event.wait(), timeout=timeout)
        duration = time.time() - start

        responses = pending_query.responses
        self.pending.remove(pending_query)

        return responses, duration

    async def SendGarage(self, request: model_pb2.GarageCommand, context) -> model_pb2.CommandResponse:
        resp, duration = await self.query(node_garage_door.open_door(request.command), timeout=1.0)
        return model_pb2.CommandResponse(status=model_pb2.OK if resp else model_pb2.TIMEOUT)

    async def CommandDevice(self, req: model_pb2.BoardLevelCommand, context) -> model_pb2.CommandResponse:
        device = devices.select(DeviceId(req.device.cls, req.device.sid))
        if device is None:
            raise Exception(f"Device doesn't exist {req.device}")

        resp, duration = await self.query(device.command(req.coc1, req.coc2, req.crl1, req.crl2), timeout=1.0)

        return model_pb2.CommandResponse(status=model_pb2.OK if resp else model_pb2.TIMEOUT)

    async def SendAlarm(self, req: model_pb2.AlarmCommand, context) -> model_pb2.CommandResponse:
        resp, duration = await self.query(node_alarm.handle_user_command(req), timeout=1.0)
        return model_pb2.CommandResponse(status=model_pb2.OK if resp else model_pb2.TIMEOUT)

    async def Reset(self, request: model_pb2.DeviceId, context) -> model_pb2.CommandResponse:
        query = Device(DeviceId(cls=request.cls, sid=request.sid)).reset()
        resp, duration = await self.query(query, timeout=1.0)
        return model_pb2.CommandResponse(status=model_pb2.OK if resp else model_pb2.TIMEOUT)

    async def QueryAttribute(self, query: CaniotMessage, timeout: float):
        response, duration = await self.query(query, timeout)

        if len(response) > 1:
            print("A broadcast query received a reponse from several devices !")

        if len(response) > 0:
            attr_response: AttributeResponse = response[0]

            return model_pb2.AttributeResponse(device=model_pb2.DeviceId(
                cls=attr_response.msgid.device_id.cls,
                sid=attr_response.msgid.device_id.sid
            ), key=attr_response.get_key(), value=attr_response.get_value(), status="OK",
                response_time=duration)
        else:
            return model_pb2.AttributeResponse(device=model_pb2.DeviceId(
                cls=query.msgid.device_id.cls,
                sid=query.msgid.device_id.sid
            ), status="TIMEOUT",
                response_time=duration)

    async def ReadAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        query = Device(DeviceId(cls=request.device.cls, sid=request.device.sid)).read_attribute(request.key)
        return await self.QueryAttribute(query, request.timeout)

    async def WriteAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        query = Device(DeviceId(cls=request.device.cls, sid=request.device.sid)).write_attribute(request.key,
                                                                                                 request.value)
        return await self.QueryAttribute(query, request.timeout)

    async def GetDevices(self, request: model_pb2.Empty, context):
        return model_pb2.Devices(device=[
            model_pb2.Device() for dev in self.devices.devices
        ])

    # allow this method to be blocking until timeout
    async def RequestTelemetry(self, request: model_pb2.TelemetryTarget, context):
        await self.query(QueryTelemetry(DeviceId(cls=request.deviceid.cls, sid=request.deviceid.sid),
                                 endpoint=request.endpoint), timeout=0.0)
        return model_pb2.Empty()

    async def GetDevice(self, request: model_pb2.Devices, context):
        dev: Device = self.devices.select(DeviceId(request.cls, request.sid))
        if dev:
            return model_pb2.Device(
                deviceid=request,
                name=dev.name,
                version=dev.version,
                status=model_pb2.Device.Status(
                    last_seen=model_pb2.DateTime(
                        seconds=int(dev.last_seen.timestamp())
                    ) if dev.last_seen is not None else None,
                    received=dev.received,
                    sent=dev.sent,
                    online=bool(dev.last_seen is not None)
                ),
                attribute=[
                    model_pb2.Attribute(key=key, value=value) for key, value in dev.attrs.items()
                ],
                **dev.get_model()
            )
        else:
            return model_pb2.Empty()


async def serve():
    server = aio.server()
    model_pb2_grpc.add_CanControllerServicer_to_server(CanController(), server)
    listen_addr = f'[::]:{configuration.grpc_port}'
    server.add_insecure_port(listen_addr)
    # TODO server.add_secure_port()
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve())
    loop.close()
