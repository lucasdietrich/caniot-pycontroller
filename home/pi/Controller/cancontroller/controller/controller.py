import asyncio
import contextlib
import logging
import time
from typing import List, Dict

import can
from grpc import aio

from cancontroller.caniot.models import gen_garage_can_command, MsgId, DeviceId, ControllerMessageBuilder, \
    ControllerMessageParser
from cancontroller.controller import initialize_can_if
from cancontroller.controller.devices import KNOWN_DEVICES
from cancontroller.ipc import model_pb2_grpc, model_pb2

logging.basicConfig()
logging.getLogger("caniot.interfaces.socketcan.socketcan").setLevel(logging.WARNING)
can_logger = logging.getLogger("caniot")
can_logger.setLevel(logging.DEBUG)
grpc_logger = logging.getLogger("grpc")
grpc_logger.setLevel(logging.DEBUG)


class PendingQuery:
    def __init__(self, query: MsgId):
        self.event = asyncio.Event()
        self.query = query
        self.response_id = None
        self.response = None

    def is_set(self) -> bool:
        if self.event.is_set():
            if self.response_id is None:
                raise Exception("event is set but response is not set")
            return True
        return False

    def check(self, response_id: MsgId, response: can.Message) -> bool:
        if response_id.is_response_of(self.query):
            self.response_id = response_id
            self.response = response
            self.event.set()
            return True
        else:
            return False


class PendingQueriesManager:
    def __init__(self):
        self.pending_queries: List[PendingQuery] = []

    async def wait_for_response(self, pending_query: PendingQuery, timeout: float) -> [bool, float]:
        self.pending_queries.append(pending_query)

        start = time.time()
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(pending_query.event.wait(), timeout)
        duration = time.time() - start

        self.pending_queries.remove(pending_query)

        return pending_query.event.is_set(), duration

    def process(self, response_id: MsgId, response: can.Message):
        for query in self.pending_queries:
            if query.check(response_id, response):
                break


class CanController(model_pb2_grpc.CanControllerServicer):
    def __init__(self, bitrate: int = 500000, controller_id: MsgId.Controller = MsgId.Controller.Main):
        self.bitrate = bitrate
        self.controller_id = controller_id
        for can_if in ["can0", "can1"]:
            initialize_can_if(can_if, bitrate=bitrate)

        self.known_devices: Dict[str, DeviceId] = KNOWN_DEVICES
        self.query_builder = ControllerMessageBuilder(self.controller_id, controller_policy=MsgId.Controller.BROADCAST)
        self.pending_queries_manager = PendingQueriesManager()

        self.can0 = can.Bus(channel='can1', bustype='socketcan')  # , receive_own_messages=True
        self.reader = can.AsyncBufferedReader()
        logger = can.Logger('logfile.asc')

        listeners = [
            self.reader,  # AsyncBufferedReader() listener
            self.handle_can_message,
            logger  # Regular Listener object
        ]

        loop = asyncio.get_event_loop()
        self.notifier = can.Notifier(self.can0, listeners, loop=loop)

        self.rx_count = 0

    def send(self, msg: can.Message):
        msgid = MsgId.from_int(msg.arbitration_id)
        can_logger.debug(f"TX {msgid} payload[{len(msg.data)}] : {msg.data}")

        return self.can0.send(msg, timeout=None)  # define global timeout

    def handle_can_message(self, msg: can.Message):
        msgid = MsgId.from_int(msg.arbitration_id)
        can_logger.debug(f"[{self.rx_count}] RX {msgid} payload[{len(msg.data)}] : {msg.data}")

        self.rx_count += 1

        self.pending_queries_manager.process(msgid, msg)

    async def SendGarage(self, request: model_pb2.GarageCommand, context) -> model_pb2.GarageResponse:
        grpc_logger.info(f"GarageResponse command={request.command}")

        self.send(gen_garage_can_command(request.command, 0, DeviceId.DataType.CRT))  # dev
        self.send(gen_garage_can_command(request.command, 1, DeviceId.DataType.CRT))  # prod
        self.send(gen_garage_can_command(request.command, 0, DeviceId.DataType.CRTAAA))  # pcb

        return model_pb2.GarageResponse(datetime=request.datetime, status="OK")

    async def ReadAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        return await self._WaitAttributeResponse(request, write=False)

    async def WriteAttribute(self, request: model_pb2.AttributeRequest, context) -> model_pb2.AttributeResponse:
        return await self._WaitAttributeResponse(request, write=True)

    async def _WaitAttributeResponse(self, request: model_pb2.AttributeRequest, write: bool = False):
        __func__ = "WriteAttribute" if write else "ReadAttribute"

        grpc_logger.info(
            f"{__func__} device={request.device.id} key={request.key}" + (f" value={request.value}" if write else ""))

        if write:
            query, canmsg = self.query_builder.WriteAttribute(DeviceId.from_int(request.device.id), request.key,
                                                              request.value)
        else:
            query, canmsg = self.query_builder.ReadAttribute(DeviceId.from_int(request.device.id), request.key)

        self.send(canmsg)

        pending_query = PendingQuery(query)
        ok, duration = await self.pending_queries_manager.wait_for_response(pending_query, timeout=request.timeout)

        value = 0
        key = 0
        if ok:
            try:
                key, value = ControllerMessageParser.ParseAttributeResponse(pending_query.response.data)
            except:
                can_logger.error("failed to parse response")
                ok = 0

            if key and key != request.key:
                can_logger.error(f"UNEXPECTED ERROR ReadAttribute response key {key} != {request.key} query key")
                ok = 0
        else:
            can_logger.error(f"response didn't get in time {query} duration={duration}")

        return model_pb2.AttributeResponse(
            device=request.device,
            key=request.key,
            value=value,
            status="OK" if ok else "NOK",
            response_time=duration
        )


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
