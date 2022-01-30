import time

from cancontroller.caniot.device import DeviceId
from cancontroller.caniot.attributes import attributes

from cancontroller.ipc import model_pb2
from cancontroller.ipc import model_pb2_grpc

from typing import Union

import grpc

# Diagnostic
# Controller aprameters, speed, ..
# Device last seen, message, stats, database
# reqest telemetry


class API:
    def __init__(self, grpc_target: str = '192.168.10.155:50051'):
        self.grpc_target = grpc_target

    def ReadAttribute(self, deviceid: DeviceId, key: int, timeout: float = 1.0) -> int:
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            response = stub.ReadAttribute(model_pb2.AttributeRequest(
                device=model_pb2.DeviceId(
                    type=deviceid.cls,
                    id=deviceid.sid
                ),
                key=key,
                timeout=timeout
            ))
            # print(model_pb2._STATUS.values_by_number[response.status].name, response.value)
            return response.value if response.status == model_pb2.OK else None

    def WriteAttribute(self, deviceid: DeviceId, key: int, value: int, timeout: float = 1.0) -> int:
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            response = stub.WriteAttribute(model_pb2.AttributeRequest(
                device=model_pb2.DeviceId(
                    type=deviceid.cls,
                    id=deviceid.sid
                ),
                key=key,
                value=value,
                timeout=timeout
            ))
            return response.value if response.status == model_pb2.OK  else None

    def SyncTime(self, deviceid: DeviceId, synctime: int = 0):
        if not synctime:
            synctime = int(time.time())

        return self.WriteAttribute(deviceid, attributes.get("time").key, synctime)

    def GetDevice(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as  channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.GetDevice(model_pb2.DeviceId(
                type=deviceid.cls,
                id=deviceid.sid
            ))

    def GetDevices(self):
        with grpc.insecure_channel(self.grpc_target) as channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            response = stub.WriteAttribute(model_pb2.Empty())
            return response

    def RequestTelemetry(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as  channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.RequestTelemetry(model_pb2.DeviceId(
                type=deviceid.cls,
                id=deviceid.sid
            ))

    def Reset(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as  channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.Reset(model_pb2.DeviceId(
                type=deviceid.cls,
                id=deviceid.sid
            ))


if __name__ == "__main__":
    api = API('192.168.10.155:50051')
    did = DeviceId(DeviceId.Class.CRTHPT, 0x03)
    response_read_attr = api.ReadAttribute(did, 0x1010)
    print(response_read_attr)