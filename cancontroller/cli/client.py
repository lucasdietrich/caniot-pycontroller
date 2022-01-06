from cancontroller.caniot.device import DeviceId

from cancontroller.ipc import model_pb2
from cancontroller.ipc import model_pb2_grpc

from typing import Union

import grpc

# Diagnostic
# Controller aprameters, speed, ..
# Device last seen, message, stats, database
# reqest telemetry


class CLIClient:
    def __init__(self, grpc_target: str):
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
            print(response)
            # print(model_pb2._STATUS.values_by_number[response.status].name, response.value)
            return response.value if response.status == "OK" else None

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
            print(response)
            return response.value if response.status == "OK" else None

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
            print(response)
            return response

    def RequestTelemetry(self, deviceid: DeviceId):
        with grpc.insecure_channel(self.grpc_target) as  channel:
            stub = model_pb2_grpc.CanControllerStub(channel)
            return stub.RequestTelemetry(model_pb2.DeviceId(
                type=deviceid.cls,
                id=deviceid.sid
            ))

if __name__ == "__main__":
    client = CLIClient('192.168.10.155:50051')
    did = DeviceId(DeviceId.cls.CRTHPT, 0x02)
    response_read_attr = client.ReadAttribute(did, 0x1010)
    response_get_device = client.GetDevice(DeviceId(5, 0))

    print(response_read_attr, response_get_device)
